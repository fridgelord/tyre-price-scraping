import unittest
from modules import sklepopon

class TestSklepOpon(unittest.TestCase):
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
    ]

    def setUp(self):
        self.sizes = [sklepopon.SklepOpon(size) for size in self.DEFAULT_SIZES]

    def test_get_address(self):
        address0 = "https://www.sklepopon.com/szukaj-opony?rozmiar=195/65R15&sezon=zimowe&producent=Hankook"
        address1 = "https://www.sklepopon.com/szukaj-opony?rozmiar=225/60R17&sezon=letnie&producent=Hankook&indeks-nosnosci=99.0&indeks-predkosci=V"
        address2 = "https://www.sklepopon.com/szukaj-opony?rozmiar=225/65R16&sezon=zimowe&producent=Laufenn&indeks-nosnosci=112.0&indeks-predkosci=R"
        address3 = "https://www.sklepopon.com/szukaj-opony?rozmiar=195/65R15&sezon=zimowe&producent=Hankook&indeks-nosnosci=91.0&indeks-predkosci=T"
        self.assertEqual(self.sizes[0]._get_address(), address0)
        self.assertEqual(self.sizes[1]._get_address(), address1)
        self.assertEqual(self.sizes[2]._get_address(), address2)
        self.assertEqual(self.sizes[3]._get_address(), address3)

    def test_get_site(self):
        text = self.sizes[1]._get_site_content( )
        self.assertNotEqual(text, "")

    def test_get_soup(self):
        self.assertNotEqual(str(self.sizes[3]._get_soup()), "")

    def test_collect(self):
        result0 = self.sizes[0].collect()
        self.assertIsNotNone(self.sizes[0].product)
        self.assertIn("195/65R15", result0[0])
        self.assertEqual("SklepOpon", result0[2])
        result1 = self.sizes[1].collect()
        self.assertEqual(type(result1[3]), float)
        self.assertGreater(result1[3], 0.0)
        result2 = self.sizes[2].collect()
        self.assertEqual("225/65R16 112/110R", result2[0])


if __name__ == "__main__":
    unittest.main()
