import data_manager as dm
import requests
from flight_data import FlightData
import os
import flights_data as fd
import flight_search as fs
import logo


def flight_search():
    print("We are going to search for all flight you add to your wish list trips.")
    search_flights = fs.FlightSearch()
    search_flights.get_data_from_sheet()
    print("Please check all flights files in flight data folder")


def add_cites_to_sheet(from_list):
    print("To which county you wish to visit?")
    to_county = dm.DataManager()
    to_county.pick_date()
    to_county.add_to_sheet(from_list)
    add_another_city = input("Do you want to add more city you wish to visit?\nType (Y)es or (N)o : ").lower()
    if add_another_city == "y" or add_another_city == "yes":
        add_cites_to_sheet(from_list)
    else:
        print("We will notify you when you got perfect deal 😊")


def add_wish_list_trip():
    print(logo.airplane)
    print("Where are you living?")
    from_country = dm.DataManager()
    from_list = (
        from_country.country, from_country.city_region_name, from_country.iata_city_code, from_country.currency_code)
    add_cites_to_sheet(from_list)


def flight_data_sheet():
    print("We are looking for all saved flight files in flight data folder.")
    FlightData()
    print("Please check your google data sheet")

def notify_me_deals():
    pass


add_wish_list_trip()
search_for_available = input("Do you want to start searching for available flight from your wish list?\n(Y)es Or (N)o.").lower()
if search_for_available == "y" or "yes":
    flight_search()
save_available_flight = input("Hi Again after checking all your trips wishes lets save it to flight sheet >>\nType C to continue").lower()
if save_available_flight == "c":
    flight_data_sheet()


'''
{'whereto': [{'to': 'United States', 'city': 'Minnesota', 'iata': 'HIB', 'fromdate': '15/03/2022', 'todate': '15/04/2022', 'price': 2000, 'currency': 'SAR', 'id': 2}, {'to': 'Sudan', 'city': 'Khartoum', 'iata': 'KRT', 'fromdate': '09/02/2022', 'todate': '15/02/2022', 'price': 1000, 'currency': 'SAR', 'id': 3}, {'to': 'United Kingdom', 'city': 'England', 'iata': 'BHX', 'fromdate': '09/02/2022', 'todate': '10/03/2022', 'price': 1000, 'currency': 'SAR', 'id': 4}]}
'''
