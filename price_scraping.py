import platform
from DataFrameAppend import *
from platforma import PlatformaOpon
import oponeo
import sklepopon
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from time import sleep
import sys
import os
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)


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

DEFAULT_INPUT = "sizes.xlsx"
DEFAULT_OUTPUT = "data.xlsx"
arguments = sys.argv
if len(sys.argv) > 1:
    input_file = sys.argv[1]
    output_file = sys.argv[2]
else:
    input_file = DEFAULT_INPUT
    output_file = DEFAULT_OUTPUT

def get_chrome_driver(hostname):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    if hostname == 'user-Vostro-260':
        chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def get_firefox_driver(hostname):
    firefox_options = Options()
    if hostname == 'user-Vostro-260':
        firefox_options.headless = True
    return webdriver.Firefox(options=firefox_options, service_log_path=os.path.join(sys.path[0], "geckodriver.log"))

driver_selector = ("-d", "--driver")
driver_options = {
    "firefox": get_firefox_driver,
    "chrome": get_chrome_driver,
    "chromium": get_chrome_driver,
}

hostname = platform.node()
for i in driver_selector:
    if i in arguments:
        position = arguments.index(i)
        driver_selected = arguments[position + 1].lower()
        try:
            driver = driver_options[driver_selected]
            driver = driver(hostname)
        except KeyError:
            print(f"Please insert one of {' '.join(driver_options.keys())} after -d or --driver")
        break
    else:
        driver = get_firefox_driver(hostname)

try:
    with open(input_file) as fp:
        temp_df = pandas.read_excel(input_file, dtype="str")
        temp_df["min_dot"] = temp_df["min_dot"].astype(int)
        sizes = temp_df.to_dict("records")
except FileNotFoundError:
    sizes = DEFAULT_SIZES



platformaopon = PlatformaOpon(driver)
results = []
for size in sizes:
    platformaopon.size = size
    results.extend(platformaopon.collect_data())
    # if size["type"] == "PCR":
    #     oponeo_results = oponeo.Oponeo(size).collect()
    #     if oponeo_results:
    #         results.append(oponeo_results)
    #     sklepopon_results = sklepopon.SklepOpon(size).collect()
    #     if sklepopon_results:
    #         results.append(sklepopon_results)

platformaopon.close()
driver.close()

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
    "DataSource",
    ],
                     )

df["WebLink"] = ""
df.append_to_excel(output_file, index=False)
