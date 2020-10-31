from bs4 import BeautifulSoup
import requests
import re
from datetime import date
import logging
from time import sleep


class InterCars():

    logger = logging.getLogger("InterCars")

    PARAM_ORDER = ["width", "profile", "seat", "brand",
                   "season(zima,lato,wielosezon)", "indeks predkosci", "indeks nosnosci"
                   ]

    SOURCE = "InterCars"
    SELLER = "InterCars B2C"

    BUY_SITE = {
        "width": "https://intercars.pl/szukaj/opony-201/?cf_szerokosc=",
        "season(zima,lato,wielosezon)": "&cf_sezon=",
        "brand": "&cf_producent=",
        "profile": "&cf_profil=",
        "seat": "&cf_srednica=",
        "indeks predkosci": "&cf_indeks-predkosci=",
        "indeks nosnosci": "&cf_indeks-nosnosci=",
    }


    PARAMS = {
        "lato": "letnia",
        "zima": "zimowa",
        "wielosezon": "całoroczna",
        "R": "170",
        "S": "180",
        "T": "190",
        "H": "210",
        "V": "240",
        "W": "270",
        "Y": "300",
    }

    def __init__(self, size):
        self.size = size.copy()
        season_short = "season(zima,lato,wielosezon)"
        self.season_original = size[season_short]
        self.size[season_short] = self.PARAMS.get(self.size[season_short], self.size[season_short] )
        self.size["brand"] = self.size["brand"].upper()
        self.size["width"] = self.size["size"].split("/")[0]
        self.size["profile"] = self.size["size"].split("/")[1].split("R")[0]
        self.size["seat"] = self.size["size"].split("R")[1] + "%22"
        LI = "indeks nosnosci"
        if LI in self.size:
            self.size[LI] = self.size[LI].replace("/", "%2F")
        SI = "indeks predkosci"
        if SI in self.size:
            s, v = self.size[SI], self.PARAMS.get(self.size[SI], "")
            self.size[SI] = f"{s}+-+{v}+km%2Fh"

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
        self.product = soup.find(True, {'class': 'gtm-item'})
        if not self.product:
            self.logger.error(f"product size {self.size['size']}, brand {self.size['brand']}: not found")
            return []
        try:
            # obligatory results
            dim = self.product.find("span", string="Rozmiar opony: ").next_sibling.text
            dim = dim.replace('"', '')
            temp_description = self.product.find("a", "prod-label").text
            brand = temp_description.split()[0].capitalize()
            pattern = temp_description.replace(brand.upper(), "")
            pattern = pattern[1:pattern.find(dim)-1]
            index = self.product.find("span", string="Indeksy: ").next_sibling.text
            dimension = dim + " " + index
            try:
                price_box = self.product.find("span", "retail-price").text.replace(",", ".")
            except AttributeError:
                price_box = self.product.find("span", "current-price nowrap").text.replace(",", ".")
            price = round(float(price_box.split()[0]) / 1.23, 2)
        except Exception:
            self.logger.exception(f"problem in size {self.size['size']}, brand {self.size['brand']}")
            return []
        try:
            dot = "DOT " + self.product.find("span", string="Rok produkcji: ").next_sibling.text.strip()
        except AttributeError:
            dot = ""
        remarks = ""
        try:
            stock = self.product.find("span", "ico-dot-text").text
        except AttributeError:
            stock = ""
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
