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
import getopt

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


USAGE = """Usage: price_scraping.py [OPTION] INPUT_FILE OUTPUT_FILE"
Simple script to scrape tyre price information from most popular Polish websites.

  -d, --driver=DRIVER       use WEBDRIVER, select firefox (default), chromium
  -s, --sources=SOURCES     download data from comma-separated list of sources,
                            default: platformaopon,oponeo,skleopon
  -c, --credentials=FILE    take platformaopon.pl credential from FILE
  -h, --help                display this message
  """

def get_options(arguments, usage):
    args = {}
    try:
        options, other_arguments = getopt.getopt(arguments,
                                                 "hd:c:s:",
                                                 ["help", "driver=", "credentials=", "sources="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for option, argument in options:
        if option in ("-h", "--help"):
            print(usage)
            sys.exit()
        if option in ("-d", "--driver"):
            args["driver_type"] = argument.lower()
        if option in ("-s", "--sources"):
            args["sources"] = argument.lower().split(",")
    if other_arguments:
        for file in other_arguments:
            if not(os.path.isfile(file)):
                print("Provide valid file", usage, sep="\n")
                sys.exit(2)
        args["input_file"] = other_arguments[0]
        args["output_file"] = other_arguments[1]
    return args


class PriceScraper():
    def __init__(self,
                 input_file="sizes.xlsx",
                 output_file="data.xlsx",
                 credentials_file="credentials.txt",
                 driver_type="firefox",
                 sources=["platformaopon", "oponeo", "sklepopon"],
                 ):
        self.input_file = input_file
        self.output_file = output_file
        self.credentials = credentials_file
        self.driver_type = driver_type
        self.sources = sources
        self.hostname = platform.node()

    @property
    def sizes(self):
        temp_df = pandas.read_excel(self.input_file, dtype="str")
        temp_df["min_dot"] = temp_df["min_dot"].astype(int)
        return temp_df.to_dict("records")

    def get_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        if self.hostname == 'user-Vostro-260':
            chrome_options.add_argument("--headless")
        return webdriver.Chrome(options=chrome_options)

    def get_firefox_driver(self):
        firefox_options = Options()
        if self.hostname == 'user-Vostro-260':
            firefox_options.headless = True
        return webdriver.Firefox(options=firefox_options,
                                 service_log_path=os.path.join(sys.path[0], "geckodriver.log"))

    def driver_option(self):
        DRIVER_OPTIONS = {
            "firefox": self.get_firefox_driver,
            "chrome": self.get_chrome_driver,
            "chromium": self.get_chrome_driver,
        }
        try:
            return DRIVER_OPTIONS[self.driver_type]
        except KeyError:
            print(f"Select proper driver from: {', '.join(DRIVER_OPTIONS.keys())}")
            sys.exit(2)

    @property
    def driver(self):
        driver = self.driver_option()
        return driver()

    def test(self):
        print(self.input_file, self.output_file, self.driver, self.credentials, sep="\n")

    def collect(self):
        self.results = []
        if "platformaopon" in self.sources:
            platformaopon = PlatformaOpon(self.driver)
        for size in self.sizes:
            if "platformaopon" in self.sources:
                platformaopon.size = size
                self.results.extend(platformaopon.collect_data())
            if size["type"] == "PCR" and "oponeo" in self.sources:
                oponeo_results = oponeo.Oponeo(size).collect()
                if oponeo_results:
                    results.append(oponeo_results)
            if size["type"] == "PCR" and "sklepopon" in self.sources:
                sklepopon_results = sklepopon.SklepOpon(size).collect()
                if sklepopon_results:
                    results.append(sklepopon_results)

        if "platformaopon" in self.sources:
            platformaopon.close()
            self.driver.close()

    def dump_data(self):
        df = DataFrameAppend(self.results, columns = [
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
        df.append_to_excel(self.output_file, index=False)

command_line_options = get_options(sys.argv[1:], USAGE)
price_scraper = PriceScraper(**command_line_options)
price_scraper.test()
