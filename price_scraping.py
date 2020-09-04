import platform
from DataFrameAppend import *
from datetime import date
import platforma
import oponeo
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import sys

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
if len(sys.argv) > 1:
    input_file = sys.argv[1]
    output_file = sys.argv[2]
else:
    input_file = DEFAULT_INPUT
    output_file = DEFAULT_OUTPUT



try:
    with open(input_file) as fp:
        ## why context manager here????
        temp_df = pandas.read_excel(input_file, dtype="str")
        temp_df["min_dot"] = temp_df["min_dot"].astype(int)
        sizes = temp_df.to_dict("records")
except FileNotFoundError:
    sizes = DEFAULT_SIZES

LOGIN_SITE = "https://platformaopon.pl/"
CREDENTIALS_FILE = "credentials.txt"


hostname = platform.node()
firefox_options = Options()
if hostname == 'user-Vostro-260':
    firefox_options.headless = True

driver = webdriver.Firefox(options=firefox_options)
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
submit_field.click()
sleep(4)

results = []
for size in sizes:
    results.extend(platforma.collect_data(size, current_date, driver))
    if size["type"] == "PCR":
        oponeo_results = oponeo.collect(size, current_date)
        if oponeo_results:
            results.extend(oponeo_results)

driver.find_element_by_xpath("//a[contains(@title, 'Wyloguj')]").click()
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
    ],
                     )

df.append_to_excel(output_file, index=False)
