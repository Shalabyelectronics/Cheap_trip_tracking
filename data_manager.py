import pandas as pd
import json
import datetime as dt
import os
import requests

SHEETY_BEARER_TOKEN = os.environ.get('cheap_trip_api')
SHEETY_END_POINT = "https://api.sheety.co/ad18ac28c260b67ca7e2e9ab98db507d/cheapTrip/whereto"
SHEET_NAME = "whereto"


class DataManager:
    def __init__(self):
        self.data_sheet = None
        self.add_to_sheet_step = None
        self.pick_date_step = None
        self.get_iata_code_step = False
        self.country = None
        self.city_region_name = None
        self.your_budget_price = None
        self.iata_city_code = None
        self.country_code = None
        self.currency_code = None
        self.get_country_code_step = True
        self.get_country_currency_code()
        self.get_iata_code()
        self.date_from_to_list = []
        self.from_date = None
        self.to_date = None
        self.sheety_api_token = SHEETY_BEARER_TOKEN
        self.sheety_end_point = SHEETY_END_POINT
        self.sheet_headers = {
            'Authorization': f"Bearer {self.sheety_api_token}"
        }
        self.sheet_name = SHEET_NAME

    def get_country_currency_code(self):
        if self.get_country_code_step:
            self.country = input("Type country name: ").title()
            country_currency_code = []
            try:
                countries_df = pd.read_csv("data/countries_codes_and_coordinates.csv")
                country_codes = countries_df[countries_df["Country"] == self.country]
                country_code = list(country_codes["Alpha-2 code"])
                # clean character from white spaces
                clean_country_code = country_code[0].strip()
                clean_country_code = clean_country_code[1:3]
                with open("data/country_currency.json", "r") as currency_file:
                    currency_data = json.load(currency_file)
                currency_code = currency_data[clean_country_code]["currency_code"]
                country_currency_code.append(clean_country_code)
                country_currency_code.append(currency_code)
                self.country_code = country_currency_code[0]
                self.currency_code = country_currency_code[1]
                self.get_iata_code_step = True
            except IndexError:
                print("Check your country name spelling.")
                self.get_country_currency_code()

    def get_iata_code(self):
        try:
            if self.get_iata_code_step:
                pd.set_option('display.max_rows', None)
                pd.set_option('max_columns', None)
                iata_data_frame = pd.read_csv("data/iata-icao.csv")
                country_code_match = iata_data_frame[iata_data_frame.country_code == self.country_code]
                print(country_code_match[["region_name", "iata", "airport"]])
                choose_iata_code = input("Please choose which city code you want:\n"
                                         "Just type the three digit iata code: ").upper()
                chosen_iata_row = country_code_match[country_code_match.iata == choose_iata_code]
                print(chosen_iata_row[["region_name", "iata", "airport"]])
                self.iata_city_code = list(chosen_iata_row.iata)[0]
                self.city_region_name = list(chosen_iata_row.region_name)[0]
                self.pick_date_step = True
            else:
                self.get_country_currency_code()
        except TypeError:
            print("Please check your spelling and try again!")
            self.get_iata_code()
        except IndexError:
            print("Please you type wrong iata code try again.")
            self.get_iata_code()

    def pick_date(self):
        if self.pick_date_step:
            date_fromto = ["From date", "To date"]
            try:
                for i in date_fromto:
                    print(i)
                    day = int(input("Type day : "))
                    month = int(input("Type month : "))
                    year = int(input("Type year : "))
                    date = dt.datetime(day=day, month=month, year=year)
                    date = date.strftime("%d/%m/%Y")
                    self.date_from_to_list.append(date)
            except ValueError as r:
                print(r)
                self.pick_date()
            else:
                self.from_date = self.date_from_to_list[0]
                self.to_date = self.date_from_to_list[1]
                self.add_to_sheet_step = True

    def add_to_sheet(self, from_list):
        from_country = from_list[0]
        from_region_name = from_list[1]
        from_iata_code_city = from_list[2]
        self.currency_code = from_list[3]
        if self.pick_date_step:
            self.your_budget_price = int(input("What is your budget price for this trip?"))
            add_row = {
                SHEET_NAME: {
                    "from":from_country,
                    "fcity":from_region_name,
                    "fiata": from_iata_code_city,
                    "to": self.country,
                    "tcity": self.city_region_name,
                    'tiata': self.iata_city_code,
                    'fromdate': self.from_date,
                    'todate': self.to_date,
                    'price': self.your_budget_price,
                    'currency': self.currency_code
                }
            }
            post_response = requests.post(self.sheety_end_point, json=add_row, headers=self.sheet_headers)
            post_response.raise_for_status()
            print("Your wish added successfully to the sheet.")

    def get_data_sheet(self):
        response = requests.get(self.sheety_end_point, headers=self.sheet_headers)
        self.data_sheet = response.json()
        return self.data_sheet

