from time import sleep
from selenium.common.exceptions import NoSuchElementException

SOURCE = "Platforma"

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


def is_old_dot(dot, min_dot):
    year = dot[-4:]
    try:
        return int(year) < min_dot
    except ValueError:
        return False


def collect_data(size, date, driver):
    """Collect information from platformaopon.pl about
    10 best offers for selected sizes

    arguments: size -> dict with obligatory keys: brand, size,
    min_qt, type, min_dot; optional: season, LI, SI, pattern, min_qt
    date

    returns: list
    """
    site = (SITE_PREFIX +
        BUY_SITE["brand"] + PARAMS_BRAND[size["brand"].lower()] + "&" +
        BUY_SITE["size"] + size["size"].replace("/", "%2F") + "&" +
        BUY_SITE["season"] + PARAMS_SEASON[size.get("season(zima,lato,wielosezon)", "").lower()] + "&" +
        BUY_SITE["LI"] + size.get("indeks nosnosci", "") + "&" +
        BUY_SITE["SI"] + PARAMS_SI[size.get("indeks predkosci", "").lower()] + "&" +
        BUY_SITE["pattern"] + size.get("bieznik(nieobowiazkowy)", "") + "&" +
        BUY_SITE["min_qt"] + size.get("min. sztuk", "") + "&" +
        SITE_SUFFIX
            )

    driver.get(site)

    offers = driver.find_elements_by_xpath("//tbody/tr")

    i = 0
    results = []
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
            date,
            brand,
            size["type"],
            size.get("season(zima,lato,wielosezon)", ""),
            SOURCE,
        ])
    sleep(8)
    return(results)
