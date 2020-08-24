from time import sleep
from datetime import date
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pandas
from DataFrameAppend import *


LOGIN_SITE = "https://platformaopon.pl/"
CREDENTIALS_FILE = "credentials.txt"
SIZES_FILE = "sizes.xlsx"

PARAMS_BRAND = {
    "hankook": "52",
    "laufenn": "18945",
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
}

PARAMS_SI = {
    "r": "22",
    "t": "24",
    "h": "26",
    "v": "27",
    "w": "28",
    "y": "29",
}

SITE_PREFIX = "https://platformaopon.pl/buy/offers?"
SITE_SUFFIX = "SaleOfferTyreFilterForm%5BisDemo%5D=0&SaleOfferTyreFilterForm%5BisRetreaded%5D=0&SaleOfferTyreFilterForm%5Bsearch%5D="

BUY_SITE = {
    "brand": "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bproducer%5D%5BpersonalizedProducersList%5D=",
    "size": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bsize%5D=",
    "season": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bseason%5D=",
    "LI": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bcapacity%5D=",
    "SI": "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bspeed%5D=",
    "pattern": "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bname%5D=",
    "min_qt": "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bamount%5D%5Bmin%5D=",
}


DEFAULT_SIZES = [
    {
    "brand": "Hankook",
    "size": "195/65R15",
    "season(zima,lato,wielosezon)": "zima",
    "indeks nosnosci": "91",
    "indeks predkosci": "T",
    "bieznik(nieobowiazkowy)": "W452",
    "min. sztuk": "20",
    "min_dot": 2019,
    "type": "PCR",
    },
]


today = date.today()
driver = webdriver.Firefox()
driver.get(LOGIN_SITE)

with open(CREDENTIALS_FILE) as fp:
    credentials = fp.read().splitlines()

try:
    with open(SIZES_FILE) as fp:
        temp_df = pandas.read_excel(SIZES_FILE, dtype="str")
        temp_df["min_dot"] = temp_df["min_dot"].astype(int)
        sizes = temp_df.to_dict("records")
except FileNotFoundError:
    sizes = DEFAULT_SIZES


def is_old_dot(dot, min_dot):
    year = dot[-4:]
    try:
        return int(year) < min_dot
    except ValueError:
        return False


username_field = driver.find_element_by_xpath("//input[contains(@id, 'username')]")
password_field = driver.find_element_by_xpath("//input[contains(@id, 'password')]")
save_me_tick = driver.find_element_by_xpath("//span[contains(@class, 'tick halflings')]")
submit_field = driver.find_element_by_xpath("//input[contains(@id, 'submit')]")

username_field.send_keys(credentials[0])
password_field.send_keys(credentials[1])
save_me_tick.click()
submit_field.click()
sleep(4)



def collect_data(size):
    results = []
    site = (SITE_PREFIX +
        BUY_SITE["brand"] + PARAMS_BRAND[size["brand"].lower()] + "&" +
        BUY_SITE["size"] + size["size"].replace("/", "%2F") + "&" +
        BUY_SITE["season"] + PARAMS_SEASON[size["season(zima,lato,wielosezon)"].lower()] + "&" +
        BUY_SITE["LI"] + size["indeks nosnosci"] + "&" +
        BUY_SITE["SI"] + PARAMS_SI[size["indeks predkosci"].lower()] + "&" +
        BUY_SITE["pattern"] + size["bieznik(nieobowiazkowy)"] + "&" +
        BUY_SITE["min_qt"] + size["min. sztuk"] + "&" +
        SITE_SUFFIX
            )

    driver.get(site)

    offers = driver.find_elements_by_xpath("//tbody/tr")
    i = 0
    for offer in offers:
        if i > 9:
            break #only need 10 resutls with proper DOT
        try:
            dimension = offer.find_element_by_xpath(".//td[contains(@class, 'tyre-size')]").text
        except NoSuchElementException:
            continue
        pattern = offer.find_element_by_xpath(".//span[contains(@class, 'model-name')]").text
        brand = offer.find_element_by_xpath(".//span[contains(@class, 'producer-name')]").text
        stock = offer.find_element_by_xpath(".//span[contains(@class, 'value')]").text
        price_str = offer.find_element_by_xpath(".//div[contains(@class, 'big-price')]").text
        price = float(price_str.replace(" zł", "").replace(",","."))
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
        if is_old_dot(dot, size["min_dot"]):
            continue
        try:
            remarks = offer.find_element_by_xpath(".//div[contains(@class, 'description')]").text
        except NoSuchElementException:
            remarks = ""

        i += 1
        results.append([
            dimension,
            pattern,
            seller,
            price,
            stock,
            dot,
            remarks,
            delivery,
            today,
            brand,
            size["type"],
            size["season(zima,lato,wielosezon)"],
        ])
    sleep(8)
    return(results)


results = []
for size in sizes:
    results.extend(collect_data(size))

df = DataFrameAppend(results, columns = [
    "size",
    "pattern",
    "seller",
    "price",
    "stock",
    "dot",
    "remarks",
    "delivery",
    "date",
    "brand",
    "type",
    "season",
    ],
)

driver.find_element_by_xpath("//a[contains(@title, 'Wyloguj')]").click()
driver.close()

df.append_to_excel("data.xlsx", index=False)
