import json, time, requests, sys, urllib3, socket, ssl
from lxml import html
from bs4 import BeautifulSoup
from html.parser import HTMLParser
api = "https://script.google.com/macros/s/AKfycbx-yKneSjj1gS_vbiGEv-mDKOd5eywt2dcIYIYSGNvacjec5dau/exec"
# "https://script.google.com/macros/s/AKfycbx-yKneSjj1gS_vbiGEv-mDKOd5eywt2dcIYIYSGNvacjec5dau/exec"
theEarlierTheBetter = 1

def sendEmail(email, message):
    data = {"email": email, "message": message}
    r = requests.post(api, json.dumps(data))
    if (r.status_code == 200):
        print("Successfully sent e-mail! :)")
    else:
        print(r.status_code, r.reason)

def mountString(best, day, month):
    return("%02d/%02d Flight " % (day, month) + best[1] + ": R$" + str(best[0]))

def searchFromLatam(day, month, origin, destination, verbose):
    latamAPI = "https://bff.latam.com/ws/proxy/booking-webapp-bff/v1/public/revenue/recommendations/oneway?country=BR&language=PT&home=pt_br&origin=%s&destination=%s&departure=2018-%02d-%02d&adult=1&cabin=Y" % (origin, destination, month, day)
    latam = requests.get(latamAPI)
    latam = json.loads(latam.content.decode())
    best = [99999, ""] # [price, flightCode]
    for flight in latam["data"]["flights"]:
        if (verbose): print("Flight: ", flight["flightCode"], " R$", flight["cabins"][0]["displayPrice"], sep='')
        if (flight["cabins"][0]["displayPrice"] < best[0]):
            best = [flight["cabins"][0]["displayPrice"], flight["flightCode"]]
    print("Best Flight Found (%02d/%02d): R$%.2lf (Flight: %s)" % (day, month, best[0], best[1]))
    print()
    return(best)

def bot(daysRange, month, targetPrice, interval, origin, destination, emails, verbose):
    bestSoFar = [99999, "", 0, 0, time.time()] # [price, flightCode, day, month, searchTime]
    while (True):
        for day in daysRange:
            try: now = searchFromLatam(day, month, origin, destination, verbose)
            except:
                print("ERROR: Couldn't connect (Retrying in %ds)" % interval)
                break
            if (now[0] <= targetPrice):
                print("YaY, better then targetPrice (%02d/%02d):" % (day, month), now)
                try:
                    for email in emails:
                        sendEmail(email, mountString(now, day, month))
                except:
                    print("ERROR: Couldn't send e-mail (Retrying in %ds)" % interval)
                    break
            if (now[0] < bestSoFar[0] or (now[0] == bestSoFar[0] and day < bestSoFar[2] and theEarlierTheBetter)):
                bestSoFar = [now[0], now[1], day, month, time.time()]
        print("Best so far: %s" % mountString([bestSoFar[0], bestSoFar[1]], bestSoFar[2], bestSoFar[3]), "| searching time: %lfs" % (time.time() - bestSoFar[4]))
        time.sleep(interval)

def readInput():
    print("First day: ", end='')
    firstDay = int(input())
    print("Last day: ", end='')
    lastDay = int(input())
    print("Month: ", end='')
    month = int(input())
    print("Threshold price: ", end='')
    thresholdPrice = int(input())
    print("Interval: ", end='')
    interval = int(input())
    print("Origin: ", end='')
    origin = input()
    print("Destination: ", end='')
    destination = input()
    print("E-mails (separated by spaces): ", end='')
    emails = input().split()
    print("Show each step (0, 1): ")
    verbose = int(input())
    return(firstDay, lastDay, month, thresholdPrice, interval, origin, destination, emails, verbose)

arguments = sys.argv
if (len(sys.argv) < 7):
    arguments = [0, 21, 26, 5, 1, 400, 600]
    arguments = [0] + list(readInput())
bot(range(int(arguments[1]), int(arguments[2]) + 1), int(arguments[3]), int(arguments[4]), float(arguments[5]), arguments[6], arguments[7], arguments[8], int(arguments[9]))
