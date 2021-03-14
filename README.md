# Price scraping 
Simple script to scrape tyre price information from most popular Polish websites.

## Usage 
`$ python price_scraping.py input_file_path.xlsx output_file_path.xlsx`

`input_file.xlsx` is an .xlsx file consisting of the following columns:
| Column name                  | Obligatory | Example        | Remarks                                                                  |
| --                           | -          | -              | -                                                                        |
| type                         | yes        | _PCR_ or _TBR_ |                                                                          |
| brand                        | yes        | _Hankook_      |
| size                         | yes        | _225/60R16_    |
| season(zima,lato,wielosezon) | yes        | _zima_         |
| indeks nosnosci              | no         | _106/104_      |
| indeks predkosci             | no         | _T_            |
| bieznik(nieobowiazkowy)      | no         | _W452_         | platformaopon.pl only                                                    |
| min. sztuk                   | no         | _16_           | Minimum number of offered tyres to be considered (platformaopon.pl only) |
| min_dot                      | no         | _2016_         | Earlies production year to be considered (platformaopon.pl only)         |
| osobowe/4x4/dostawcze        | no         | _dostawcze_    | Obligatory for oponeo.pl                                                 |

Pricing information is dumped into `output_file.xlsx`. 

## Websites ##
The following websites are supported:
- [oponeo.pl](https://www.oponeo.pl)
- [sklepopon.pl](https://www.sklepopon.pl)
- [platformaopon.pl](https://www.platformaopon.pl)
- [intercars.pl](https://intercars.pl)

In case of B2C sites the first record in listing (usually lowest price with sufficient stock) is recorded.
For platformaopon.pl 10 best offers fulfilling requirements from `input_file.xlsx` are selected.

### platformaopon.pl ###
In order to use this website you need to provide credentials in `credentials.py` in `modules` directory. The file should contain two lines:
~~~
login="login"
password="password"
~~~
