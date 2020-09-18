import telegram
import requests
import json
import time
import threading 
from datetime import datetime
from Adafruit_IO import Client
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='aa47b938d6034147888855be260a14e7')

stop_threads = False
aio = Client('naveen1000', '935bf537f26444ffb0e3a7990427ad55')
base = "https://api.telegram.org/bot1228033872:AAHsI3oFOQLKVC7mmnVH0bNyQuPGitiBEXQ/"

def get_updates(offset=None):
        url = base + "getUpdates?timeout=100"
        if offset:
            url = url + "&offset={}".format(offset + 1)
        try:
            print(url)
            r = requests.get(url)
            return json.loads(r.content)
        except:
            return None

def send_message(msg, chat_id):
        url = base + "sendMessage?chat_id={}&text={}".format(chat_id, msg)
        if msg is not None:
            try:
                requests.get(url)
            except:
                pass

def send_time():
    while True:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M")
        print("date and time =", dt_string)
        aio.send('message', dt_string)
        #send_message(dt_string,'582942300')
        time.sleep(30)
        global stop_threads 
        if stop_threads:
            print('Stopped Time')
            break

def corona():
    raw = requests.get('https://api.covid19india.org/data.json')
    cdata = raw.json()   
    statewise = cdata['statewise']
    msg = "Corona Data"
    for i in statewise:
        state = i['state']
        if state == "Andhra Pradesh":
            active = i['active']
            confirmed = i['confirmed']
            deaths = i['deaths']
            recovered = i['recovered']
            state = i['state']
            lastupdatedtime = i['lastupdatedtime']
            msg= msg +  "-AP" +" "
            msg= msg + "Act:" + active +"  "
            msg= msg + "Conf:" + confirmed +"  "
            msg= msg + "Dead:" + deaths +"  "
            msg= msg + "Rec:" + recovered +"  "
            break
    print(msg)        
    aio.send('message', msg)

def cricket(mid):
    while True:
        try:
            source=requests.get('http://mapps.cricbuzz.com/cbzios/match/'+mid+'/leanback.json')
            data = source.json()
            bat = data['bat_team']['name']
            bow = data['bow_team']['name']
            score=int(data["comm_lines"][0]["score"])
            wicket=int(data["comm_lines"][0]["wkts"])
            over=float(data['bat_team']['innings'][0]['overs'])
            detailed_score=data["comm_lines"][0]["score"]+"/"+data["comm_lines"][0]["wkts"]+" "+data['bat_team']['innings'][0]['overs']
            try:
                bowler=data['bowler'][0]['name']
                batname0=data['batsman'][0]['name']
                batname1=data['batsman'][1]['name']
                bat0score=data['batsman'][0]['r']
                bat1score=data['batsman'][1]['r']
                bat0ball=data['batsman'][0]['b']
                bat1ball=data['batsman'][1]['b']
                bowler=bow +":"+data['bowler'][0]['name']
                batters=batname0+"("+bat0score+"-"+bat0ball+")"+batname1+"("+bat1score+"-"+bat1ball+")"
                detailed_score=bat+":"+data["comm_lines"][0]["score"]+"/"+data["comm_lines"][0]["wkts"]+" "+data['bat_team']['innings'][0]['overs']
            except:
                print("An exception occurred fetching either batters or bowler")
            try:
                txt=bowler+" "+batters
                print(detailed_score + " " + txt)
                aio.send('message', detailed_score + " " + txt)
            except:
                print("An exception occurred sending")
        except:
                print("An exception occurred start")
        time.sleep(10)
        global stop_threads 
        if stop_threads:
            print('Stopped Cricket')
            break

def news():
    news = []
    data_hindu = newsapi.get_top_headlines(sources='the-hindu',
                                            language='en')

    articles = data_hindu['articles']
    for article in articles:
        #print(article['title'])
        news.append(article['title'])

    data_toi = newsapi.get_top_headlines(sources='the-times-of-india',
                                            language='en')

    articles = data_toi['articles']
    for article in articles:
        #print(article['title'])
        news.append(article['title'])

    data_google = newsapi.get_top_headlines(sources='google-news-in',
                                            language='en')

    articles = data_google['articles']
    for article in articles:
        #print(article['title'])
        news.append(article['title'])
    for msg in news:
        aio.send('message',msg)
        print(msg)
        time.sleep(15)
        if stop_threads:
            print('Stopped News')
            break



def main():            
    send_message('Mcu Server started!','582942300')
    update_id = None
    while True:
        try:
            updates = get_updates(offset=update_id)   
            updates = updates["result"]
            print('.')
        except:
            updates=None

        if updates:
            global stop_threads
            stop_threads = True
            for item in updates:
                print('*')
                update_id = item["update_id"]
                from_ = item["message"]["from"]["id"]
                try:
                    data = str(item["message"]["text"])
                    print(data)
                except:
                    data = None
                    continue
                if data == 'time':
                    try:
                        stop_threads = False
                        t1 = threading.Thread(target=send_time)
                        t1.start() 
                    except:
                        print("exception occured in time ")
                if data[:7] == 'display':
                        try:
                            aio.send('message', data[8:])
                            send_message('Displayed ' + data[8:],'582942300')
                        except:
                            print("exception occured in display ")
                if data == 'corona':
                        try:
                            corona()
                            send_message('Displayed Corona Data','582942300')
                        except:
                            print("exception occured in Corona ")
                if data[:7] == 'cricket':
                        try:
                            mid = str(data[8:])
                            send_message('Displayed cricket' + mid ,'582942300')
                            stop_threads = False
                            t1 = threading.Thread(target=cricket , args=(mid,))
                            t1.start()                             
                        except:
                            print("exception occured in cricket ")
                if data == 'news':
                        try:
                            send_message('Displayed news' ,'582942300')
                            stop_threads = False
                            t1 = threading.Thread(target=news)
                            t1.start() 
                        except:
                            print("exception occured in news ")
                print('done')

try:
    main()
except:
    time.sleep(5)
    main()



