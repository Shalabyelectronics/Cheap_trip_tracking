import requests
import os
import json
import notification_manager as nm

SHEETY_BEARER_TOKEN = os.environ.get('cheap_trip_api')
SHEETY_END_POINT = "https://api.sheety.co/ad18ac28c260b67ca7e2e9ab98db507d/cheapTrip/whereto"
SHEET_NAME = "whereto"


class FlightSearch:
    def __init__(self):
        self.trip_price = None
        self.your_budget = None
        self.data_sheet = None
        self.sheety_api_token = SHEETY_BEARER_TOKEN
        self.sheety_end_point = SHEETY_END_POINT
        self.sheet_headers = {
            'Authorization': f"Bearer {self.sheety_api_token}"
        }
        self.sheet_name = SHEET_NAME
        self.to_city = None
        self.from_city = None
        self.flight_data_file_path = None
        self.kiwi_api_key = os.environ["KIWI_API_KEY"]
        self.kiwi_search_end_point = "https://tequila-api.kiwi.com/v2/search"
        self.headers = {
            "apikey": self.kiwi_api_key
        }
        self.flight_search_data = None

    def request_flight_data(self, parameters_dict, object_id):
        try:
            response = requests.get(self.kiwi_search_end_point, params=parameters_dict, headers=self.headers)
            response.raise_for_status()
        except Exception as r:
            r = str(r)
            error_list = r.split()
            if error_list[0] == '422':
                print(f"There is no flight from {self.from_city} to the city destination {self.to_city}.")
                self.is_available_trip('No', object_id)
        else:
            self.flight_search_data = response.json()
            if len(self.flight_search_data['data']) > 0:
                self.create_flight_file()
                self.is_available_trip('Yes', object_id)
                # Get the price from the search flight data
                self.trip_price = self.flight_search_data["data"][0]["price"]
                if self.trip_price < self.your_budget:
                    # Send an email with the flight details by using Notification class
                    nm.NotificationManager(self.flight_search_data, self.your_budget)


    def create_flight_file(self):
        try:
            from_to_city = f"{self.from_city.lower()}_{self.to_city.lower()}"
            path = f"flights_data/{from_to_city}_flight_data.json"
        except AttributeError as r:
            print(r)
        else:
            with open(path, "w") as flight_data_file:
                json.dump(self.flight_search_data, flight_data_file, indent=4)
                self.flight_data_file_path = path

    def get_data_from_sheet(self):
        response = requests.get(self.sheety_end_point, headers=self.sheet_headers)
        self.data_sheet = response.json()['whereto']
        data_sheet_list = self.data_sheet
        for data in data_sheet_list:
            self.from_city = data['fcity']
            self.to_city = data['tcity']
            self.your_budget = data['price']
            row_id = data['id']
            parameters_dict = {
                "fly_from": data['fiata'],
                "fly_to": data['tiata'],
                "curr": data['currency'],
                "date_from": data['fromdate'],
                "date_to": data['todate']
            }
            self.request_flight_data(parameters_dict, row_id)

    def is_available_trip(self, yes_or_no, object_id):
        try:
            edit_available = {
                self.sheet_name: {
                    'available': yes_or_no
                }
            }
            response = requests.put(f"{self.sheety_end_point}/{object_id}", json=edit_available,
                                    headers=self.sheet_headers)
            response.raise_for_status()
        except Exception as r:
            print(r)
        else:
            print("successfully edit")

    def compare_price(self, your_budget, trip_price):
        if trip_price < your_budget:
            print("Send me the trip details with the booking link")
        else:
            print(f"Trip price not under your budget right now.")

