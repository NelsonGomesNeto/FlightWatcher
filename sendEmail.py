import json
import time
import requests
import urllib3
from lxml import html
from bs4 import BeautifulSoup
from html.parser import HTMLParser
api = "https://script.google.com/macros/s/AKfycbx-yKneSjj1gS_vbiGEv-mDKOd5eywt2dcIYIYSGNvacjec5dau/exec"

def sendEmail(message):
    data = {"link": message}
    r = requests.post(api, json.dumps(data))
    if (r.status_code == 200):
        print("Successfully sent e-mail! :)")
    else:
        print(r.status_code, r.reason)

def mountString(best, day, month):
    return("%02d/%02d Flight " % (day, month) + best[1] + ": R$" + str(best[0]))

def searchFromLatam(day, month, showAll):
    latamAPI = "https://bff.latam.com/ws/proxy/booking-webapp-bff/v1/public/revenue/recommendations/oneway?country=BR&language=PT&home=pt_br&origin=MCZ&destination=CWB&departure=2018-%02d-%02d&adult=1&cabin=Y" % (month, day)
    #print(latamAPI)
    latam = requests.get(latamAPI)
    latam = json.loads(latam.content.decode())
    best = [99999, 0]
    for flight in latam["data"]["flights"]:
        if (showAll): print("Flight: ", flight["flightCode"], " R$", flight["cabins"][0]["displayPrice"], sep='')
        if (flight["cabins"][0]["displayPrice"] < best[0]):
            best = [flight["cabins"][0]["displayPrice"], flight["flightCode"]]
    print("Best Flight Found (%02d/%02d):" % (day, month), best)
    print()
    return(best)

def bot(daysRange, month, showAll, targetPrice, interval):
    while (True):
        bestSoFar = [99999, 0, 0, 0]
        for i in daysRange:
            now = searchFromLatam(i, month, showAll)
            if (now[0] <= targetPrice):
                print("YaY, better then targetPrice (%02d/%02d):" % (i, month), now)
                sendEmail(mountString(now, i, month))
            if (now[0] < bestSoFar[0]):
                bestSoFar = [now[0], now[1], i, month]
        print("Best so far: %s" % mountString([bestSoFar[0], bestSoFar[1]], bestSoFar[2], bestSoFar[3]))
        time.sleep(interval)

bot(range(21, 26 + 1), 5, 1, 400, 60 * 10)
