from bs4 import BeautifulSoup
import requests
import re

def collect(size, date):
    PARAMS = {
        "lato": "letnie",
        "zima": "zimowe",
        "wielosezon": "caloroczne",
    }

    size_reordered = [
        PARAMS.get(size["season(zima,lato,wielosezon)"]),
        size["brand"],
        size["size"].replace("/", "-").replace("R", "-r"),
        size["indeks predkosci"],
        size["indeks nosnosci"],
    ]

    BUY_SITE = [
        "https://www.oponeo.pl/wybierz-opony/s=1/",
        "/p=1/",
        "/r=1/",
        "/ip=1/",
        "/in=1/",
    ]

    site = ""
    for parameter, site_part in zip(size_reordered, BUY_SITE):
        site += site_part + parameter

    htm = requests.get(site).text
    soup = BeautifulSoup(htm, "html.parser")
    product = soup.find(True, {'class': 'product container'})
    brand = product.find("span", "producer").text
    pattern = product.find("span", "model").text
    dim = product.find("span", "size").text.replace(" ", "")
    li = product.find(attrs={"data-tp": "TireLoadIndex"}).em.text
    si = product.find(attrs={"data-tp": "TireSpeedIndex"}).em.text
    dimension = dim + " " + li + si
    try:
        dot = "DOT " + product.find("span", "srot").text.split()[-1]
    except AttributeError:
        dot = ""
    stock = product.find(attrs={"data-tp": "StockLevel"})["data-tpd"]
    stock = re.findall("@MSG': '(.*)'", stock)[0]
    price = round(float(product.find("span", "price size-3").text) / 1.23, 2)
    delivery = ""
    remarks = ""
    seller = "Oponeo"

    return [[
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
    ]]
