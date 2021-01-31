import platform
from .DataFrameAppend import *
from .platforma import PlatformaOpon
from . import oponeo
from . import sklepopon
from . import intercars
from . import credentials
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from time import sleep
import sys
import os
import logging
import getopt

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)

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
        if len(other_arguments) != 2:
            sys.exit(f"Provide two filenames \n\n{usage}")
        if not(os.path.isfile(other_arguments[0])):
            sys.exit(f"Provide valid input filename \n\n{usage}")
        args["input_file"] = other_arguments[0]
        args["output_file"] = other_arguments[1]
    return args


class PriceScraper():
    logger = logging.getLogger("PriceScraper")

    DEFAULT_SOURCES = ["platformaopon", "oponeo", "sklepopon", "intercars"]

    def __init__(self,
                 input_file="data/input/sizes.xlsx",
                 output_file="data/output/data.xlsx",
                 credentials_file="credentials.txt",
                 driver_type="firefox",
                 sources=DEFAULT_SOURCES,
                 ):
        self.input_file = input_file
        self.output_file = output_file
        self.credentials = credentials_file
        self.driver_type = driver_type
        for source in sources:
            if source.lower() not in self.DEFAULT_SOURCES:
                raise Exception(f"Source \"{source}\" incorrect,"
                                f" must be one of: {', '.join(self.DEFAULT_SOURCES)}")
        self.sources = [i.lower() for i in sources]
        self.hostname = platform.node()
        self.results = []


    @property
    def sizes(self):
        temp_df = pandas.read_excel(self.input_file, dtype="str")
        temp_df["min_dot"] = temp_df["min_dot"].astype(int)
        return temp_df.to_dict("records")

    def get_chrome_driver(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--window-size=1920,1080")
        if self.hostname == 'user-Vostro-260':
            chrome_options.add_argument("--headless")
        return webdriver.Chrome(options=chrome_options)

    def get_firefox_driver(self):
        firefox_options = FirefoxOptions()
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
            sys.exit(f"Driver \"{self.driver_type}\" incorrect."
                     f" Select proper driver from: {', '.join(DRIVER_OPTIONS)}")

    @property
    def driver(self):
        driver = self.driver_option()
        return driver()

    def _collect_sklepopon(self, size):
        sklepopon_results = sklepopon.SklepOpon(size).collect()
        if sklepopon_results:
            self.results.append(sklepopon_results)

    def _collect_intercars(self, size):
        resutls = intercars.InterCars(size).collect()
        if resutls:
            self.results.append(resutls)

    def _collect_oponeo(self, size):
        oponeo_results = oponeo.Oponeo(size).collect()
        if oponeo_results:
            self.results.append(oponeo_results)

    def collect(self):
        if "platformaopon" in self.sources:
            platformaopon = PlatformaOpon(self.driver, credentials.login, credentials.password)
        for size in self.sizes:
            if "platformaopon" in self.sources:
                platformaopon.size = size
                self.results.extend(platformaopon.collect())
            if size["type"] == "PCR" and "oponeo" in self.sources:
                self._collect_oponeo(size)
            if size["type"] == "PCR" and "sklepopon" in self.sources:
                self._collect_sklepopon(size)
            if size["type"] == "PCR" and "intercars" in self.sources:
                self._collect_intercars(size)
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


def main():
    command_line_options = get_options(sys.argv[1:], USAGE)
    price_scraper = PriceScraper(**command_line_options)
    price_scraper.collect()
    price_scraper.dump_data()


if __name__ == "__main__":
    main()
