import json
import os
import requests


SHEETY_BEARER_TOKEN = os.environ.get('cheap_trip_api')
SHEETY_END_POINT = "https://api.sheety.co/ad18ac28c260b67ca7e2e9ab98db507d/cheapTrip/flightdata"
SHEET_NAME = "flightdatum"


class FlightData:
    def __init__(self):
        self.route_stop_point = None
        self.route_details = None
        self.flight_files = os.listdir("flights_data")
        self.sheety_cheap_trip_api = SHEETY_BEARER_TOKEN
        self.sheety_end_point_api = SHEETY_END_POINT
        self.sheety_headers = {
                'Authorization': f"Bearer {self.sheety_cheap_trip_api}"
            }
        self.route_step_list = []
        self.route_stop_points_details = []
        self.read_flights_files()

    def read_json_file(self, file):
        with open(f"flights_data/{file}", 'r') as flight_file:
            return json.load(flight_file)

    def check_airline_name(self, airline_list):
        airlines_names = []
        with open("data/airlines.json", "r") as airline_codes_file:
            airline_data = json.load(airline_codes_file)
            for airline in airline_list:
                if airline in airline_data:
                    airlines_names.append((airline, airline_data[airline]))
        return airlines_names

    def get_routes_details(self):
        self.route_step_list = []
        self.route_stop_points_details = []
        route_step = 1
        for route in self.route_details:
            from_route_city = route["cityFrom"]
            route_airline = route["airline"]
            to_route_city = route["cityTo"]
            local_departure_dt = route["local_departure"]
            utc_departure_dt = route["utc_departure"]
            local_arrival_dt = route["local_arrival"]
            utc_arrival_dt = route["utc_arrival"]
            data = {
                route_step: {
                    "from_route_city": from_route_city,
                    "route_airline": route_airline,
                    "to_route_city": to_route_city,
                    "local_departure_dt": local_departure_dt,
                    "utc_departure_dt": utc_departure_dt,
                    "local_arrival_dt": local_arrival_dt,
                    "utc_arrival_dt": utc_arrival_dt
                }
            }
            self.route_stop_points_details.append(data)
            self.route_step_list.append(route_step)
            route_step += 1

    def save_to_google_sheet(self, row):
        try:
            post_response = requests.post(self.sheety_end_point_api, json=row, headers=self.sheety_headers)
            post_response.raise_for_status()
        except Exception as r:
            print(r)
        else:
            print("row successfully added")

    def read_flights_files(self):
        for file in self.flight_files:
            flight_data = self.read_json_file(file)
            # flight_from_country = flight_data["data"][0]["countryFrom"]["name"]
            # flight_to_country = flight_data["data"][0]["countryTo"]["name"]
            iata_from_city = flight_data["data"][0]["flyFrom"]
            flight_from_city = flight_data["data"][0]["cityFrom"]
            flight_to_city = flight_data["data"][0]["cityTo"]
            iata_to_city = flight_data["data"][0]["flyTo"]
            trip_price = flight_data["data"][0]["price"]
            airlines_list = flight_data["data"][0]["airlines"]
            currency = flight_data["currency"]
            # airlines_names = self.check_airline_name(airlines_list)
            self.route_details = flight_data["data"][0]["route"]
            self.route_stop_point = len(self.route_details)
            self.route_stop_points_details = []
            self.get_routes_details()
            # utc_departure = self.route_stop_points_details[0][self.route_step_list[0]]["utc_departure_dt"]
            # utc_arrival = self.route_stop_points_details[-1][self.route_step_list[-1]]["utc_arrival_dt"]
            booking_link = flight_data["data"][1]["deep_link"]
            add_row = {
                SHEET_NAME: {
                    'flyfrom': flight_from_city,
                    'flyto': flight_to_city,
                    'iatafromcode': iata_from_city,
                    'iatatocode': iata_to_city,
                    'tripprice': trip_price,
                    'currency': currency,
                    'booklink': booking_link

                }
            }
            self.save_to_google_sheet(add_row)


'''
Reduce data because sheety can't handle post too much data
'departuretime': utc_departure,
'arrivaltime': utc_arrival,
'link': booking_link,
'airlines': airlines_names,
'from': flight_from_country,
'to': flight_to_country,
'''