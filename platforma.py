from time import sleep
from datetime import date
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pandas


LOGIN_SITE = "https://platformaopon.pl/"
CREDENTIALS_FILE = "credentials.txt"
SIZES_FILE = "sizes.csv"

PARAMS = {
    "hankook": "52",
    "lato": "1",
    "zima": "2",
    "całoroczne": "3",
    "wielosezon": "3",
    "summer": "1",
    "winter": "2",
    "all-season": "3",
    "all-weather": "3",
    "t": "24",
    "h": "26",
    "v": "27",
    "w": "28",
    "y": "29",
}

SITE_PREFIX = "https://platformaopon.pl/buy/offers?"
SITE_SUFFIX = "SaleOfferTyreFilterForm%5BisDemo%5D=0&SaleOfferTyreFilterForm%5BisRetreaded%5D=0&SaleOfferTyreFilterForm%5Bsearch%5D="

BUY_SITE = [
    "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bproducer%5D%5BpersonalizedProducersList%5D=",
    "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bsize%5D=",
    "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bseason%5D=",
    "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bcapacity%5D=",
    "SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bspeed%5D=",
    "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bname%5D=",
    "SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bamount%5D%5Bmin%5D=20&",
]


DEFAULT_SIZES = [
    ["Hankook", "195/65R15", "zima", "91", "T", "W452", "20",],
    ["Hankook", "205/55R16", "zima", "91", "T", "W452", "20",],
]


driver = webdriver.Firefox()
driver.get(LOGIN_SITE)

with open(CREDENTIALS_FILE) as fp:
    credentials = fp.read().splitlines()

try:
    with open(SIZES_FILE) as fp:
        sizes = [line.split(";") for line in fp.read().splitlines()[1:]]
except FileNotFoundError:
    sizes = DEFAULT_SIZES

username_field = driver.find_element_by_xpath("//input[contains(@id, 'username')]")
password_field = driver.find_element_by_xpath("//input[contains(@id, 'password')]")
save_me_tick = driver.find_element_by_xpath("//span[contains(@class, 'tick halflings')]")
submit_field = driver.find_element_by_xpath("//input[contains(@id, 'submit')]")

username_field.send_keys(credentials[0])
password_field.send_keys(credentials[1])
save_me_tick.click()
submit_field.click()
sleep(4)

results = []
for size in sizes:
    site = ""
    for key, item in enumerate(size):
        if key != 1:
            item = item.lower().replace("/", "%2F")
        site += BUY_SITE[key] + PARAMS.get(item, item) + "&"
    final_site = SITE_PREFIX + site + SITE_SUFFIX
    driver.get(final_site)


    offers = driver.find_elements_by_xpath("//tbody/tr")
    for offer in offers:
        try:
            size = offer.find_element_by_xpath(".//td[contains(@class, 'tyre-size')]").text
        except NoSuchElementException:
            continue
        pattern = offer.find_element_by_xpath(".//span[contains(@class, 'model-name')]").text
        stock = offer.find_element_by_xpath(".//span[contains(@class, 'value')]").text
        price_str = offer.find_element_by_xpath(".//div[contains(@class, 'big-price')]").text
        price = float(price_str.replace(" zł", "").replace(",","."))
        try:
            seller = offer.find_element_by_xpath(".//img[contains(@class, 'company-logo')]").get_attribute("title")
        except NoSuchElementException:
            seller = offer.find_element_by_xpath(".//div[contains(@class, 'company-table-row__name')]").text
        delivery = offer.find_element_by_xpath(".//div[contains(@class, 'delivery-time delivery-time-info')]").text
        try:
            dot = offer.find_element_by_xpath(".//div[contains(@class, 'tyre-year')]").text
        except NoSuchElementException:
            dot = ""
        try:
            remarks = offer.find_element_by_xpath(".//div[contains(@class, 'description')]").text
        except NoSuchElementException:
            remarks = ""

        results.append([
            size,
            pattern,
            seller,
            price,
            stock,
            dot,
            remarks,
            date.today(),
        ])
    sleep(8)

print(results)
driver.find_element_by_xpath("//a[contains(@title, 'Wyloguj')]").click()
driver.close()

df = pandas.DataFrame(results,
                      columns = [
                          "size",
                          "pattern",
                          "seller",
                          "price",
                          "stock",
                          "dot",
                          "remarks",
                          "date",
                      ],
                      )

df.to_excel("data.xlsx", index=False)





