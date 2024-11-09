from bs4 import BeautifulSoup
import requests
import smtplib
import os
from dotenv import load_dotenv
import Database
load_dotenv()
with open("credentials.txt","r") as file:
    list = file.readlines()
for i in list:
    l = i.split(",")
    l1 = Database.loadproductsdb(l[0])
    for j in l1:
        live_url = j[2]
        response = requests.get(live_url, headers={"Accept-Language": "en-US,en;q=0.9",
                                                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"})

        soup = BeautifulSoup(response.content, "html.parser")
        print(soup.prettify())

        # Find the HTML element that contains the price
        price = soup.find(class_="Nx9bqj CxhGGd").get_text()
        # Convert to floating point number
        price_as_float = price[1:].split(",")
        price_as_float = int("".join(price_as_float))
        print(price_as_float)
        title = soup.find(class_="VU-ZEz").get_text().strip()
        print(title)

        # Set the price below which you would like to get a notification
        BUY_PRICE = j[3]

        if price_as_float < BUY_PRICE:
            message = f"{title} is on sale for {price}!"

            with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
                connection.starttls()
                result = connection.login(os.environ["EMAIL"], os.environ["PASSWORD"])
                connection.sendmail(
                    from_addr=os.environ["EMAIL"],
                    to_addrs=l[2],
                    msg=f"Subject:Amazon Price Alert!\n\n{message}\n{live_url}".encode("utf-8")
                )
        day = Database.accesslasttrackeddaydb(l[0],j[0])
        if day:
            Database.addpricehistorydb(l[0],j[0],price_as_float,day[-1][-1]+1)
        else:
            Database.addpricehistorydb(l[0], j[0], price_as_float,0)

