from bs4 import BeautifulSoup
import requests
import re
from datetime import date
import logging
from time import sleep


class SklepOpon():

    logger = logging.getLogger("SklepOpon")

    PARAM_ORDER = ["size", "season(zima,lato,wielosezon)", "brand",
                    "indeks nosnosci" ,"indeks predkosci", ]

    SOURCE = "SklepOpon"
    SELLER = "SklepOpon"

    BUY_SITE = {
        "size": "https://www.sklepopon.com/szukaj-opony?rozmiar=",
        "season(zima,lato,wielosezon)": "&sezon=",
        "brand": "&producent=",
        "indeks nosnosci": "&indeks-nosnosci=",
        "indeks predkosci": "&indeks-predkosci=",
    }


    PARAMS = {
        "lato": "letnie",
        "zima": "zimowe",
        "wielosezon": "całoroczne",
    }

    def __init__(self, size):
        self.size = size.copy()
        season_short = "season(zima,lato,wielosezon)"
        self.season_original = size[season_short]
        self.size[season_short] = self.PARAMS.get(self.size[season_short], self.size[season_short] )
        self.size["brand"] = self.size["brand"].capitalize()
        LI = "indeks nosnosci"
        if LI in self.size:
            self.size[LI] = self.size[LI].split("/")[0] + ".0"

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
        self.product = soup.find(True, {"data-c-name": "listing-products-element"})
        if not self.product:
            self.logger.error(f"product size {self.size['size']}, brand {self.size['brand']}: not found")
            return []
        try:
            # obligatory results
            brand = self.product.find("span", "text-p6d xl:text-p4d flex items-center font-bold").text.strip()
            description = self.product.find("span", "font-normal text-p4d").text.strip()
            try:
                dim_l = description.split()
                dimension = dim_l[-4] + dim_l[-3] + " " + dim_l[-2] + dim_l[-1]
                pattern = " ".join(dim_l[:-4])
            except IndexError:
                dimension = description
                pattern = ""
            price_1 = self.product.find("span", "text-p1d").text
            price_2 = self.product.find("span", "text-p3d pr-2").text
            price = "".join((price_1, price_2)).replace(",", ".")
            price = round(float(price.split()[0]) / 1.23, 2)
        except Exception:
            self.logger.exception(f"problem in size {self.size['size']}, brand {self.size['brand']}")
            return []
        try:
            dot = "DOT " + self.product.find("p", "prd_prod_date").text
        except AttributeError:
            dot = ""
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
