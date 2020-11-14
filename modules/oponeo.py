from bs4 import BeautifulSoup
import requests
import re
from datetime import date
import logging
from time import sleep


class Oponeo():

    logger = logging.getLogger("Oponeo")

    PARAM_ORDER = ["season(zima,lato,wielosezon)", "osobowe/4x4/dostawcze",
                   "brand", "size", "indeks predkosci", "indeks nosnosci"]

    SOURCE = "Oponeo"
    SELLER = "Oponeo B2C"

    BUY_SITE = {
        "season(zima,lato,wielosezon)": "https://www.oponeo.pl/wybierz-opony/s=1/",
        "osobowe/4x4/dostawcze": "/t=1/",
        "brand": "/p=1/",
        "size": "/r=1/",
        "indeks predkosci": "/ip=1/",
        "indeks nosnosci": "/in=1/",
    }

    PARAMS = {
        "lato": "letnie",
        "zima": "zimowe",
        "wielosezon": "caloroczne",
    }

    def __init__(self, size):
        self.size = size.copy()
        season_short = "season(zima,lato,wielosezon)"
        self.season_original = size[season_short]
        self.size[season_short] = self.PARAMS.get(self.size[season_short], self.size[season_short] )
        self.size["size"] = self.size["size"].upper().replace("/", "-").replace("R", "-r")
        LI = "indeks nosnosci"
        if LI in self.size:
            self.size[LI] = self.size[LI].replace("/", "-")

    def _parameter_given(self, parameter):
        return parameter in self.size

    def _get_address(self):
        address = []
        for parameter in self.PARAM_ORDER:
            if self._parameter_given(parameter):
                address.append(self.BUY_SITE[parameter])
                address.append(self.size[parameter])
        return "".join(address).lower()

    def _get_site_content(self):
        sleep(4)
        return requests.get(self._get_address()).text

    def _get_soup(self):
        return BeautifulSoup(self._get_site_content(), "html.parser")

    def _get_short_stock(self, text):
        ask = "Zapytaj o dostępnosć"
        if text == ask:
            return text
        pattern1 = "Ponad ([0-9]+) sztuk"
        pattern2 = "Ostatni. ([0-9]+) sztuk"
        try:
            stockmatch1= re.match(pattern1, text)
            stockmatch2= re.match(pattern2, text)
            if stockmatch1:
                return ">" + stockmatch1.groups()[0]
            else:
                return stockmatch2.groups()[0]
        except Exception:
            self.logger.exception(f"Different stock type: {text}")
            return text


    def collect(self):
        soup = self._get_soup()
        self.product = soup.find(True, {'class': 'product container'})
        if not self.product:
            self.logger.error(f"product size {self.size['size']}, brand {self.size['brand']}: not found")
            return []
        try:
            # obligatory results
            pattern = self.product.find("span", "model").text
            brand = self.product.find("span", "producer").text
            dim = self.product.find("span", "size").text.replace(" ", "")
            li = self.product.find(attrs={"data-tp": "TireLoadIndex"}).em.text
            si = self.product.find(attrs={"data-tp": "TireSpeedIndex"}).em.text
            dimension = dim + " " + li + si
            price = round(float(self.product.find("span", "price size-3").text) / 1.23, 2)
        except Exception:
            self.logger.exception(f"problem in size {self.size['size']}, brand {self.size['brand']}")
            return []
        try:
            dot = "DOT " + self.product.find("span", "srot").text.split()[-1]
        except AttributeError:
            dot = ""
        try:
            long_stock = self.product.find(attrs={"data-tp": "StockLevel"})["data-tpd"]
            long_stock = re.findall(r"@MSG': '(.*)'", long_stock)[0]
            stock = self._get_short_stock(long_stock)
        except Exception:
            self.logger.exception(f"stock problem in size {self.size['size']}, brand {self.size['brand']}")
            stock = ""
        delivery = ""
        remarks = ""

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
