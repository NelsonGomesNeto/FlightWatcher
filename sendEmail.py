import json
import requests
import urllib3
from lxml import html
from bs4 import BeautifulSoup
from html.parser import HTMLParser
api = "https://script.google.com/macros/s/AKfycbx-yKneSjj1gS_vbiGEv-mDKOd5eywt2dcIYIYSGNvacjec5dau/exec"

def sendEmail(link):
    data = {"link": link}
    r = requests.post(api, json.dumps(data))
    if (r.status_code == 200):
        print("Successfully sent e-mail! :)")
    else:
        print(r.status_code, r.reason)

def mountString(best):
    return("Flight " + best[1] + ": R$" + str(best[0]))

def searchFromLatam():
    latamAPI = "https://bff.latam.com/ws/proxy/booking-webapp-bff/v1/public/revenue/recommendations/oneway?country=BR&language=PT&home=pt_br&origin=MCZ&destination=CWB&departure=2018-05-23&adult=1&cabin=Y"
    latam = requests.get(latamAPI)
    latam = json.loads(latam.content.decode())
    best = [99999, 0]
    for flight in latam["data"]["flights"]:
        print("Flight: ", flight["flightCode"], " R$", flight["cabins"][0]["displayPrice"], sep='')
        if (flight["cabins"][0]["displayPrice"] < best[0]):
            best = [flight["cabins"][0]["displayPrice"], flight["flightCode"]]
    print("Best Flight Found:", best)
    sendEmail("Latam %s" % mountString(best))

searchFromLatam()

