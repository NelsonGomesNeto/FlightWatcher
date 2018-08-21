import json, time, requests, sys, urllib3, socket, ssl
from datetime import date, timedelta
# from lxml import html
# from html.parser import HTMLParser
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

def dateString(nowDate):
    return("%02d/%02d/%04d" % (nowDate.day, nowDate.month, nowDate.year))

def mountString(flightInfo, nowDate):
    return("%s Flight " % (dateString(nowDate)) + flightInfo[1] + ": R$" + str(flightInfo[0]))

def searchFromLatam(nowDate, origin, destination, verbose):
    latamAPI = "https://bff.latam.com/ws/proxy/booking-webapp-bff/v1/public/revenue/recommendations/oneway?country=BR&language=PT&home=pt_br&origin=%s&destination=%s&departure=%04d-%02d-%02d&adult=1&cabin=Y" % (origin, destination, nowDate.year, nowDate.month, nowDate.day)
    latam = requests.get(latamAPI)
    latam = json.loads(latam.content.decode())
    best = [99999.99, ""] # [price, flightCode]
    for flight in latam["data"]["flights"]:
        if (verbose): print("Flight: ", flight["flightCode"], " R$", flight["cabins"][0]["displayPrice"], sep='')
        if (flight["cabins"][0]["displayPrice"] < best[0]):
            best = [flight["cabins"][0]["displayPrice"], flight["flightCode"]]
    print("Best Flight Found: %s\n" % (mountString(best, nowDate)))
    return(best)

def bot(startingDate, endingDate, thresholdPrice, interval, origin, destination, emails, verbose):
    bestSoFar = [99999.99, "", date(2015,6,8), time.time()] # [price, flightCode, date, searchTime]
    while (True):
        nowDate = startingDate
        while (nowDate != endingDate + timedelta(1)):
            try:
                searchedFlight = searchFromLatam(nowDate, origin, destination, verbose)
                if (searchedFlight[0] <= thresholdPrice):
                    print("YaY, better then threshold price:", mountString(searchedFlight, nowDate))
                    try:
                        for email in emails:
                            sendEmail(email, mountString(searchedFlight, nowDate))
                    except Exception as e:
                        print("ERROR (%s): Couldn't send e-mail (Retrying in %.0lfs)" % (str(e), interval))
                if (searchedFlight[0] < bestSoFar[0] or (theEarlierTheBetter and searchedFlight[0] == bestSoFar[0] and nowDate < bestSoFar[2])):
                    bestSoFar = [searchedFlight[0], searchedFlight[1], nowDate, time.time()]
            except Exception as e:
                print("ERROR (%s): Couldn't send e-mail (Retrying in %.0lfs)" % (str(e), interval))
            nowDate += timedelta(1)
        print("Best so far: %s" % mountString([bestSoFar[0], bestSoFar[1]], bestSoFar[2]), "| searching time: %lfs" % (time.time() - bestSoFar[3]))
        time.sleep(interval)

def readDate():
    day, month, year = list(map(int, input().split('/')))
    return(date(year, month, day))

def readInput():
    print("Starting date (day/month/year): ", end='')
    startingDate = readDate()
    print("Ending date (dat/month/year): ", end='')
    endingDate = readDate()
    print("Threshold price: ", end='')
    thresholdPrice = float(input())
    print("Interval: ", end='')
    interval = float(input())
    print("Origin: ", end='')
    origin = input()
    print("Destination: ", end='')
    destination = input()
    print("E-mails (separated by spaces): ", end='')
    emails = input().split()
    print("Show each step (0, 1): ")
    verbose = int(input())
    return(startingDate, endingDate, thresholdPrice, interval, origin, destination, emails, verbose)

bot(*list(readInput()))
