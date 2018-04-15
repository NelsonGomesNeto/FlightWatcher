import json, time, requests, sys, urllib3, socket, ssl
from lxml import html
from bs4 import BeautifulSoup
from html.parser import HTMLParser
api = "https://script.google.com/macros/s/AKfycbx-yKneSjj1gS_vbiGEv-mDKOd5eywt2dcIYIYSGNvacjec5dau/exec"
DISABLED = 1

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
    bestSoFar = [99999, 0, 0, 0, time.time()]
    while (True):
        for i in daysRange:
            try: now = searchFromLatam(i, month, showAll)
            except:
                print("ERROR: Couldn't connect (Retrying in %ds)" % interval)
                break
            if (now[0] <= targetPrice):
                print("YaY, better then targetPrice (%02d/%02d):" % (i, month), now)
                try: sendEmail(mountString(now, i, month))
                except:
                    print("ERROR: Couldn't send e-mail")
                    break
            if (now[0] < bestSoFar[0] or (now[0] == bestSoFar[0] and i < bestSoFar[2] and DISABLED)):
                bestSoFar = [now[0], now[1], i, month, time.time()]
        print("Best so far: %s" % mountString([bestSoFar[0], bestSoFar[1]], bestSoFar[2], bestSoFar[3]), "%lfs" % (time.time() - bestSoFar[4]))
        time.sleep(interval)

arguments = sys.argv
if (len(sys.argv) < 7):
    arguments = [0, 21, 26, 5, 1, 320, 600]
bot(range(int(arguments[1]), int(arguments[2]) + 1), int(arguments[3]), int(arguments[4]), float(arguments[5]), int(arguments[6]))
