import unittest
from modules import oponeo
from time import sleep

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
            "osobowe/4x4/dostawcze": "dostawcze",
        }
    ]

    def setUp(self):
        self.sizes = [oponeo.Oponeo(size) for size in self.DEFAULT_SIZES]

    def test_get_address(self):
        address0 = "https://www.oponeo.pl/wybierz-opony/s=1/zimowe/t=1/osobowe/p=1/hankook/r=1/195-65-r15"
        address1 = "https://www.oponeo.pl/wybierz-opony/s=1/letnie/t=1/4x4/p=1/hankook/r=1/225-60-r17/ip=1/v/in=1/99"
        address2 = "https://www.oponeo.pl/wybierz-opony/s=1/zimowe/t=1/dostawcze/p=1/laufenn/r=1/225-65-r16/ip=1/r/in=1/112-110"
        address3 = "https://www.oponeo.pl/wybierz-opony/s=1/zimowe/t=1/osobowe/p=1/hankook/r=1/195-65-r15/ip=1/t/in=1/91"
        self.assertEqual(self.sizes[0]._get_address(), address0)
        self.assertEqual(self.sizes[1]._get_address(), address1)
        self.assertEqual(self.sizes[2]._get_address(), address2)
        self.assertEqual(self.sizes[3]._get_address(), address3)

    def test_get_site(self):
        sleep(1)
        text = self.sizes[1]._get_site_content( )
        self.assertNotEqual(text, "")

    def test_get_soup(self):
        sleep(1)
        self.assertNotEqual(str(self.sizes[3]._get_soup()), "")

    def test_get_short_stock(self):
        text1 = "Ponad 4 sztuki w magazynie"
        text2 = "Ostatnie 4 sztuki w magazynie"
        text3 = "Zapytaj o dostępnosć"
        result1 = self.sizes[0]._get_short_stock(text1)
        result2 = self.sizes[0]._get_short_stock(text2)
        result3 = self.sizes[0]._get_short_stock(text3)
        self.assertEqual(result1, ">4")
        self.assertEqual(result2, "4")
        self.assertEqual(result3, text3)

    def test_collect(self):
        sleep(1)
        result0 = self.sizes[0].collect()
        self.assertIsNotNone(self.sizes[0].product)
        self.assertIn("195/65R15", result0[0])

        sleep(1)
        result1 = self.sizes[1].collect()
        self.assertGreater(result1[3], 0.0)

        sleep(1)
        result2 = self.sizes[2].collect()
        self.assertEqual("225/65R16 112/110R", result2[0])

        sleep(1)
        result4 = self.sizes[4].collect()
        self.assertIsNone(self.sizes[4].product)
        self.assertEqual(result4, [])


if __name__ == "__main__":
    unittest.main()
