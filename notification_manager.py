import os
from email.message import EmailMessage
import smtplib

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
RECIPIENT_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASS = os.environ.get("SENDER_PASS")
SMTP_SERVER = {
    "smtp": "smtp.gmail.com"
    , "port": 465
}


class NotificationManager:
    def __init__(self, flight_data, your_budget):
        self.message = None
        self.flight_data = flight_data
        self.fly_from = self.flight_data['data'][0]["cityFrom"]
        self.fly_to = self.flight_data['data'][0]["cityTo"]
        self.trip_price = self.flight_data['data'][0]["price"]
        self.currency = self.flight_data["currency"]
        self.flight_booking_link = self.flight_data["data"][1]["deep_link"]
        self.your_budget = your_budget
        self.create_message()
        self.send_email()

    def create_message(self):
        self.message = f"We found a great deal to travel from {self.fly_from} to {self.fly_to}\n" \
                       f"As your chosen budget was {self.your_budget} and the ticket price is {self.trip_price}\n" \
                       f"For more details check the booking link below\n" \
                       f"{self.flight_booking_link}\n" \
                       f"Wish you nice trip 😊 "

    def send_email(self):
        msg = EmailMessage()
        msg["Subject"] = f"Perfect Deal to {self.fly_to} ✈"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content(self.message)
        with smtplib.SMTP_SSL(SMTP_SERVER["smtp"], SMTP_SERVER["port"]) as connection:
            connection.login(SENDER_EMAIL, SENDER_PASS)
            connection.send_message(msg)
            print("We found a perfect deal for you please check your email.")
