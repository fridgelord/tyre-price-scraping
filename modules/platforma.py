from time import sleep
from selenium.common.exceptions import NoSuchElementException
import os
import sys
from selenium.common.exceptions import TimeoutException
from datetime import date


class PlatformaOpon:

    SOURCE = "PlatformaOpon"
    LOGIN_SITE = "https://platformaopon.pl/login"
    PARAMS_BRAND = {
        "hankook": "52",
        "laufenn": "18945",
        "michelin": "4",
        "goodyear": "3",
        "continental": "2",
        "pirelli": "13",
        "dunlop": "9",
        "bridgestone": "18",
        "kleber": "11",
        "bfgoodrich": "7",
        "bf goodrich": "7",
        "semperit": "57",
        "uniroyal": "5",
        "fulda": "10",
        "firestone": "17",
        "debica": "6",
        "dębica": "6",
        "sava": "14",
        "kingstar": "53",
        "kormoran": "12",
        "barum": "1",
        "nexen": "90",
        "dayton": "16",
    }
    PARAMS_SEASON = {
        "lato": "1",
        "zima": "2",
        "całoroczne": "3",
        "wielosezon": "3",
        "summer": "1",
        "winter": "2",
        "all-season": "3",
        "all-weather": "3",
        "": "",
    }
    PARAMS_SI = {
        "r": "22",
        "t": "24",
        "h": "26",
        "v": "27",
        "w": "28",
        "y": "29",
        "": "",
    }
    SITE_PREFIX = "https://platformaopon.pl/buy/offers?"
    SITE_SUFFIX = ("SaleOfferTyreFilterForm%5BisDemo%5D=0&SaleOfferTyreFilterForm%5"
                   "BisRetreaded%5D=0&SaleOfferTyreFilterForm%5Bsearch%5D=")
    BUY_SITE = {
        "brand": "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bproducer%5D%5BpersonalizedProducersList%5D=",
        "size": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bsize%5D=",
        "season(zima,lato,wielosezon)": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bseason%5D=",
        "indeks nosnosci": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bcapacity%5D=",
        "indeks predkosci": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bspeed%5D=",
        "bieznik(nieobowiazkowy)": "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bname%5D=",
        "min. sztuk": "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bamount%5D%5Bmin%5D=",
    }
    PARAM_ORDER = ["brand", "size", "season(zima,lato,wielosezon)",
                   "indeks nosnosci", "indeks predkosci", "bieznik(nieobowiazkowy)",
                   "min. sztuk", ]

    def __init__(self, driver, login, password):
        self.driver = driver
        self.driver.get(self.LOGIN_SITE)
        username_field = self.driver.find_element_by_xpath("//input[contains(@id, 'username')]")
        password_field = self.driver.find_element_by_xpath("//input[contains(@id, 'password')]")
        save_me_tick = self.driver.find_element_by_xpath("//span[contains(@class, 'tick halflings')]")
        submit_field = self.driver.find_element_by_xpath("//input[contains(@id, 'submit')]")
        username_field.send_keys(login)
        password_field.send_keys(password)
        save_me_tick.click()
        try:
            submit_field.click()
        except TimeoutException:
            # for some reason webdriver thinks the page doesn't load
            pass
        sleep(4)

    def close(self):
        try:
            self.driver.find_element_by_xpath("//a[contains(@title, 'Wyloguj')]").click()
        except TimeoutException:
            # for some reason webdriver thinks the page doesn't load
            pass

    def is_old_dot(self, dot):
        year = dot[-4:]
        try:
            return int(year) < self._min_dot
        except ValueError:
            return False

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size.copy()
        self._description = " ".join([size['brand'], size['size'],
                             (f"{size.get('indeks nosnosci', '')}"
                              f"{size.get('indeks predkosci', '')}")]
                                                     )
        self._type = size.get("type", "")
        self._brand = size.get("brand", "")
        self._min_dot = int(size.get("min_dot", 0))
        self._season = size.get("season(zima,lato,wielosezon)", "")
        self._size["brand"] = self.PARAMS_BRAND.get(self._size["brand"].lower())
        self._size["season(zima,lato,wielosezon)"] = (
            self.PARAMS_SEASON.get(self._size["season(zima,lato,wielosezon)"].lower()))
        if "indeks predkosci" in self._size:
            self._size["indeks predkosci"] = self.PARAMS_SI.get(self._size["indeks predkosci"].lower())
        self._size["size"] = self._size["size"].replace("/", "%2F")

    @property
    def address(self):
        address = []
        for parameter in self.PARAM_ORDER:
            if parameter in self.size:
                address.append(self.BUY_SITE[parameter] + self.size[parameter])
        address.append(self.SITE_SUFFIX)
        return self.SITE_PREFIX + "&".join(address)

    def _get_data(self, offer):
        try:
            dimension = offer.find_element_by_xpath(".//td[contains(@class, 'tyre-size')]").text
        except NoSuchElementException:
            return []
        pattern = offer.find_element_by_xpath(".//span[contains(@class, 'model-name')]").text
        brand = offer.find_element_by_xpath(".//span[contains(@class, 'producer-name')]").text
        stock = offer.find_element_by_xpath(".//span[contains(@class, 'value')]").text
        price_str = offer.find_element_by_xpath(".//div[contains(@class, 'big-price')]").text
        price = float("".join(price_str.replace(" zł", "").replace(",",".")))
        try:
            seller = offer.find_element_by_xpath(".//img[contains(@class, 'company-logo')]").get_attribute("title")
        except NoSuchElementException:
            seller = offer.find_element_by_xpath(".//div[contains(@class, 'company-table-row__name')]").text
        delivery = offer.find_element_by_xpath(".//div[contains(@class, 'delivery-time delivery-time-info')]").text
        delivery = delivery[9:]
        try:
            dot = offer.find_element_by_xpath(".//div[contains(@class, 'tyre-year')]").text
        except NoSuchElementException:
            dot = ""
        if self.is_old_dot(dot):
            return []
        try:
            remarks = offer.find_element_by_xpath(".//div[contains(@class, 'description')]").text
        except NoSuchElementException:
                remarks = ""
        return [
            dimension,
            pattern,
            seller,
            price,
            stock,
            dot,
            remarks,
            delivery,
            date.today(),
            self._brand,
            self._type,
            self._season,
            self.SOURCE,
        ]

    def collect(self):
        """Collect information from platformaopon.pl about
        10 best offers for selected size

        returns: list
        """

        self.driver.get(self.address)
        offers = self.driver.find_elements_by_xpath("//tbody/tr")
        i = 0
        results = []
        for offer in offers:
            if i > 9:
                # only need 10 resutls with proper DOT
                break
            data = self._get_data(offer)
            if data:
                i += 1
                results.append(data)
        sleep(4)
        return results
