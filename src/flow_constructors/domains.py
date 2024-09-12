import os


def get_site_code(key):
    domain_vs_site_code = {"ef": "ef",
                           "mt": "mt",
                           "sdsp": "wt",
                           "sdz": "wv",
                           "owo": "wd",
                           "totr": "tt",
                           "llfl": "lf",
                           "at": "at",
                           "tp": "tp",
                           "dm": "dm",
                           "bp": "bp",
                           "llny": "nw",
                           "llca": "lc",
                           "ww": "ww",
                           "ub": "ub",
                           "ll": "ll",
                           "ch": "ch",
                           "hp": "hp",
                           "ba": "ba",
                           "lb": "lb",
                           "lg": "lg",
                           "dl": "lg",
                           "la": "la",
                           "lv": "lv",
                           "aq": "aq",
                           "ps": "ps",
                           "pp": "pp",
                           "wb": "wb",
                           "ht": "ht",
                           "fo": "fo",
                           "wa": "wa",
                           "lm": "lm",
                           "af": "af",
                           "ty": "ty",
                           "bv": "bv",
                           "rt": "rt",
                           "uc": "uc",
                           "ud": "ud"}
    return domain_vs_site_code[key].upper()


def get_park_full_name(park_short_name):
    get_park_full_name_dictionary = {"mt": "Madame Tussauds London",
                                     "at": "Alton Towers Resort",
                                     "ht": "Warner Bros. Studio Tour London",
                                     "wb": "Warner Bros. Hollywood",
                                     "ps": "Park of Poland - Suntago",
                                     "ub": "Butlins Skegness Holiday Park",
                                     "pp": "Paultons Park and Peppa Pig World",
                                     "tp": "Thorpe Park Resort",
                                     "nw": "LEGOLAND New York",
                                     "sdsp": "San Diego Zoo Safari Park",
                                     "totr": "Top Of The Rock",
                                     "bp": "Blackpool Pleasure Beach",
                                     "llfl": "LEGOLAND Florida",
                                     "sdz": "San Diego Zoo",
                                     "ef": "Efteling",
                                     "lg": "LEGOLAND Deutschland",
                                     "ch": "Chessington World of Adventures",
                                     "dm": "Drayton Manor Resort",
                                     "lb": "LEGOLAND® Billund",
                                     "ll": 'LEGOLAND Windsor',
                                     "fu": "Futuroscope Theme Park",
                                     "av": "Six Flags Magic Mountain",
                                     "dq": "Six Flags Fiesta Texas",
                                     "aj": "Six Flags Great Adventure",
                                     "ag": "Six Flags Over Georgia"}

    return get_park_full_name_dictionary[park_short_name]


def get_angela_login_credentials(key):
    credentials = {"user": "qa.serviceaccount_automation@pomvom.com",
                   "password": os.environ.get('selenium_qa_email_service_account_password')}
    return credentials[key]


def get_uuid_status(key):
    uuid_assignment = {"jpg_pairs": "jpg_pairs",
                       "all_files_same_uuid": "all_files_same_uuid",
                       "pre_association_in_meta_data": "pre_association_in_meta_data",
                       "origin_uuid_in_meta_data": "origin_uuid_in_meta_data"}
    return uuid_assignment[key]
