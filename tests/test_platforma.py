import unittest
import modules.platforma
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from datetime import datetime

class TestOponeo(unittest.TestCase):
    DEFAULT_SIZES = [
        {
            "brand": "Hankook",
            "size": "195/65R15",
            "season(zima,lato,wielosezon)": "zima",
            "type": "PCR",
            "osobowe/4x4/dostawcze": "osobowe",
        },
        {
            "brand": "Hankook",
            "size": "225/60R17",
            "season(zima,lato,wielosezon)": "lato",
            "indeks nosnosci": "99",
            "indeks predkosci": "V",
            "bieznik(nieobowiazkowy)": "K125",
            "min. sztuk": "20",
            "min_dot": 2019,
            "type": "PCR",
            "osobowe/4x4/dostawcze": "4x4",
        },
        {
            "brand": "Laufenn",
            "size": "225/65R16",
            "season(zima,lato,wielosezon)": "zima",
            "indeks nosnosci": "112/110",
            "indeks predkosci": "R",
            "bieznik(nieobowiazkowy)": "LY31",
            "min. sztuk": "20",
            "min_dot": 2019,
            "type": "PCR",
            "osobowe/4x4/dostawcze": "dostawcze",
        },
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
            "osobowe/4x4/dostawcze": "osobowe",
        },
        {
            "brand": "Hankook",
            "size": "195/65R15",
            "season(zima,lato,wielosezon)": "zima",
            "type": "PCR",
            "indeks nosnosci": "110/112",
            "osobowe/4x4/dostawcze": "dostawcze",
        }
    ]

    def setUp(self):
        options = ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        self.platforma_opon = platforma.PlatformaOpon(self.driver)

    def tearDown(self):
        self.platforma_opon.close()
        self.driver.close()

    def test_get_address(self):
        addresses = (
            "https://platformaopon.pl/buy/offers?SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bproducer%5D%5BpersonalizedProducersList%5D=52&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bsize%5D=195%2F65R15&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bseason%5D=2&SaleOfferTyreFilterForm%5BisDemo%5D=0&SaleOfferTyreFilterForm%5BisRetreaded%5D=0&SaleOfferTyreFilterForm%5Bsearch%5D=",
            "https://platformaopon.pl/buy/offers?SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bproducer%5D%5BpersonalizedProducersList%5D=52&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bsize%5D=225%2F60R17&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bseason%5D=1&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bcapacity%5D=99&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bspeed%5D=27&SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bname%5D=K125&SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bamount%5D%5Bmin%5D=20&SaleOfferTyreFilterForm%5BisDemo%5D=0&SaleOfferTyreFilterForm%5BisRetreaded%5D=0&SaleOfferTyreFilterForm%5Bsearch%5D=",
            "https://platformaopon.pl/buy/offers?SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bproducer%5D%5BpersonalizedProducersList%5D=18945&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bsize%5D=225%2F65R16&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bseason%5D=2&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bcapacity%5D=112/110&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bspeed%5D=22&SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bname%5D=LY31&SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bamount%5D%5Bmin%5D=20&SaleOfferTyreFilterForm%5BisDemo%5D=0&SaleOfferTyreFilterForm%5BisRetreaded%5D=0&SaleOfferTyreFilterForm%5Bsearch%5D=",
            "https://platformaopon.pl/buy/offers?SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bproducer%5D%5BpersonalizedProducersList%5D=52&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bsize%5D=195%2F65R15&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bseason%5D=2&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bcapacity%5D=91&SaleOfferTyreFilterForm%5BtyreParameters%5D%5Bspeed%5D=24&SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bname%5D=W452&SaleOfferTyreFilterForm%5Bsale_offer%5D%5Bamount%5D%5Bmin%5D=20&SaleOfferTyreFilterForm%5BisDemo%5D=0&SaleOfferTyreFilterForm%5BisRetreaded%5D=0&SaleOfferTyreFilterForm%5Bsearch%5D=",
        )
        for size, address in zip(self.DEFAULT_SIZES, addresses):
            self.platforma_opon.size = size
            self.assertEqual(self.platforma_opon.address, address)

    def test_collect(self):
        self.platforma_opon.size = self.DEFAULT_SIZES[0]
        result0 = self.platforma_opon.collect()
        self.assertIn("195/65R15", result0[0][0])
        self.assertIn("195/65R15", result0[9][0])

        self.platforma_opon.size = self.DEFAULT_SIZES[1]
        result1 = self.platforma_opon.collect()
        self.assertGreater(result1[4][3], 0.0)
        for data in result1:
            dot = datetime.now().year if data[5] == "" else int(data[5][-4:])
            self.assertGreater(dot, self.DEFAULT_SIZES[1]["min_dot"] - 1)
        self.platforma_opon.size = self.DEFAULT_SIZES[2]
        result2 = self.platforma_opon.collect()
        self.assertEqual("225/65R16 112/110R", result2[1][0])

        self.platforma_opon.size = self.DEFAULT_SIZES[4]
        result4 = self.platforma_opon.collect()
        self.assertEqual(result4, [])


if __name__ == "__main__":
    unittest.main()
