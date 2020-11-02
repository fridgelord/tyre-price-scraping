from bs4 import BeautifulSoup
import requests
import re
from datetime import date
import logging
from time import sleep


class SklepOpon():

    logger = logging.getLogger("SklepOpon")

    PARAM_ORDER = ["width", "profile", "seat", "indeks predkosci", "indeks nosnosci"
                     , "season(zima,lato,wielosezon)", "brand", ]

    SOURCE = "SklepOpon"
    SELLER = "SklepOpon"

    BUY_SITE = {
        "width": "https://www.sklepopon.com/opony?strona=1&filtr[szerokosc]=",
        "season(zima,lato,wielosezon)": "&filtr[sezon]=",
        "brand": "&filtr[producers]=",
        "profile": "&filtr[profil]=",
        "seat": "&filtr[srednica]=",
        "indeks predkosci": "&filtr[si]=",
        "indeks nosnosci": "&filtr[li]=",
    }


    PARAMS = {
        "lato": "1",
        "zima": "2",
        "wielosezon": "3",
        "Hankook": "38",
        "Laufenn": "266",
    }

    def __init__(self, size):
        self.size = size.copy()
        season_short = "season(zima,lato,wielosezon)"
        self.season_original = size[season_short]
        self.size[season_short] = self.PARAMS.get(self.size[season_short], self.size[season_short] )
        self.size["brand"] = self.PARAMS.get(self.size["brand"], self.size["brand"] )
        self.size["width"] = self.size["size"].split("/")[0]
        self.size["profile"] = self.size["size"].split("/")[1].split("R")[0]
        self.size["seat"] = self.size["size"].split("R")[1]
        LI = "indeks nosnosci"
        if LI in self.size:
            self.size[LI] = self.size[LI].replace("/", "%2F")

    def _parameter_given(self, parameter):
        return parameter in self.size

    def _get_address(self):
        address = []
        for parameter in self.PARAM_ORDER:
            if self._parameter_given(parameter):
                address.append(self.BUY_SITE[parameter])
                address.append(self.size[parameter])
        return "".join(address)

    def _get_site_content(self):
        sleep(4)
        agent = "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0"
        headers = {"User-Agent": agent}
        return requests.get(self._get_address(), headers=headers).text

    def _get_soup(self):
        return BeautifulSoup(self._get_site_content(), "html.parser")

    def collect(self):
        soup = self._get_soup()
        self.product = soup.find(True, {'class': 'listingContainer'})
        if not self.product:
            self.logger.error(f"product size {self.size['size']}, brand {self.size['brand']}: not found")
            return []
        try:
            # obligatory results
            pattern = self.product.find("span", "bierznik").text #sic!
            brand = self.product.find("span", "producent").text
            dim = self.product.find("span", "rozmiar").text
            try:
                dim_l = dim.split()
                dimension = dim_l[0] + dim_l[1] + " " + dim_l[2] + dim_l[3]
            except IndexError:
                dimension = dim
            price_box = self.product.find("p", "prd_priceBox").text
            price = round(float(price_box.split()[0]) / 1.23, 2)
        except Exception:
            self.logger.exception(f"problem in size {self.size['size']}, brand {self.size['brand']}")
            return []
        try:
            dot = "DOT " + self.product.find("span", "prd_prod_date").find("span", "data").text
        except AttributeError:
            dot = ""
        try:
            remarks = self.product.find("span", "prd_prod_date").find("span", "custom_msg").text
        except AttributeError:
            remarks = ""
        stock = "40"
        delivery = ""

        return [
            dimension,
            pattern,
            self.SELLER,
            price,
            stock,
            dot,
            remarks,
            delivery,
            date.today(),
            brand,
            self.size["type"],
            self.season_original,
            self.SOURCE,
        ]
