import platform
from DataFrameAppend import *
from datetime import date
import platforma
import oponeo
import sklepopon
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from time import sleep
import sys
import os
import logging
import getopt

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)

current_date = date.today()

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

USAGE = """Usage: price_scraping.py [OPTION] INPUT_FILE OUTPUT_FILE"
Simple script to scrape tyre price information from most popular Polish websites.

  -c, --credentials=FILE    take platformaopon.pl credential from FILE
  -h, --help                display this message
  """

def get_options(arguments):
    input_file = DEFAULT_INPUT
    output_file = DEFAULT_OUTPUT
    try:
        options, other_arguments = getopt.getopt(arguments, "h", "--help")
    except getopt.GetoptError:
        print(USAGE)
        sys.exit(2)
    for option, argument in options:
        if option in ("-h", "--help"):
            print(USAGE)
            sys.exit()
    if other_arguments:
        for file in other_arguments:
            if not(os.path.isfile(file)):
                print("Provide valid file\n", USAGE)
                sys.exit(2)
        input_file = other_arguments[0]
        output_file = other_arguments[1]
    return input_file, output_file

input_file, output_file = get_options(sys.argv[1:])

try:
    with open(input_file) as fp:
        ## why context manager here????
        temp_df = pandas.read_excel(input_file, dtype="str")
        temp_df["min_dot"] = temp_df["min_dot"].astype(int)
        sizes = temp_df.to_dict("records")
except FileNotFoundError:
    sizes = DEFAULT_SIZES

LOGIN_SITE = "https://platformaopon.pl/login"
CREDENTIALS_FILE = os.path.join(sys.path[0], "credentials.txt")


hostname = platform.node()
firefox_options = Options()
if hostname == 'user-Vostro-260':
    firefox_options.headless = True

driver = webdriver.Firefox(options=firefox_options, service_log_path=os.path.join(sys.path[0], "geckodriver.log"))
driver.get(LOGIN_SITE)

with open(CREDENTIALS_FILE) as fp:
    credentials = fp.read().splitlines()

username_field = driver.find_element_by_xpath("//input[contains(@id, 'username')]")
password_field = driver.find_element_by_xpath("//input[contains(@id, 'password')]")
save_me_tick = driver.find_element_by_xpath("//span[contains(@class, 'tick halflings')]")
submit_field = driver.find_element_by_xpath("//input[contains(@id, 'submit')]")

username_field.send_keys(credentials[0])
password_field.send_keys(credentials[1])
save_me_tick.click()
try:
    submit_field.click()
except TimeoutException:
    pass # for some reason webdriver thinks the page doesn't load

sleep(4)

results = []
for size in sizes:
    results.extend(platforma.collect_data(size, current_date, driver))
    if size["type"] == "PCR":
        oponeo_results = oponeo.Oponeo(size).collect()
        if oponeo_results:
            results.append(oponeo_results)
        sklepopon_results = sklepopon.SklepOpon(size).collect()
        if sklepopon_results:
            results.append(sklepopon_results)

try:
    driver.find_element_by_xpath("//a[contains(@title, 'Wyloguj')]").click()
except TimeoutException:
    pass # for some reason webdriver thinks the page doesn't load
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
