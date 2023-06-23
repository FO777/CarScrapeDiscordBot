import requests
import cloudscraper
import helheim
from helheim.exceptions import (
    HelheimException,
    HelheimSolveError,
    HelheimRuntimeError,
    HelheimSaaSError,
    HelheimSaaSBalance,
    HelheimVersion,
    HelheimAuthError
)
import bs4 as bs
import lxml
from replit import db
import os
import concurrent.futures
import random
from time import sleep
import email
import smtplib
from keep_alive import keep_alive

my_helauth = os.environ['helauth']
helheim.auth(my_helauth)
keep_alive()

proxylist = []
vin = False
miles = 0

def injection(session, response):
    if helheim.isChallenge(session, response):
        # solve(session, response, max_tries=5)
        return helheim.solve(session, response)
    else:
        return response


def extract(proxy):
  global working_proxy
  try:
      cloudsession.proxies = {
         'http':proxy,
         'https':proxy
      }
      url = 'https://httpbin.org/ip'
      cloudsession.get(url, timeout=30)
      print("working proxy : "+proxy)
      working_proxy.append(proxy)
      return proxy
  except:
      return 


def make_proxy():
  global proxylist
  global working_proxy
  global ogip
  if len(working_proxy) > 0:
      cloudsession.proxies = {
       'http':"http://"+ogip,
       'https':"http://"+ogip
    }
      get_proxy = cloudsession.get('https://free-proxy-list.net/')
  else:
      get_proxy = cloudsession.get('https://free-proxy-list.net/')
  soup = bs.BeautifulSoup(get_proxy.content, "lxml")
  finding = soup.find_all(class_="table table-striped table-bordered")
  string_finding = str(finding[0].find('tbody'))
  separating = list(string_finding.split('</tr>'))
  proxylist = []
  for n in separating:
      try:
          helper = n.split('<td>')
          https = helper[4].split('<td')
          if 'yes' in https[2]:
              proxylist.append('http://'+helper[1][:-5]+':'+helper[2][:-5])
      except:
          pass


cloudsession = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome', # we want a chrome user-agent
                'mobile': False, # pretend to be a desktop by disabling mobile user-agents
                'platform': 'windows' # pretend to be 'windows' or 'darwin' by only giving this type of OS for user-agents
            },
            requestPostHook=injection,
            # Add a hCaptcha provider if you need to solve hCaptcha
             captcha={
                 'provider': 'vanaheim' # use 'vanaheim' for built in solver, dont need api key param
             }
        )

ip = cloudsession.get('https://httpbin.org/ip', timeout=30).content
ipstring = str(ip)
ipstart = ipstring.find("origin")
ipend = ipstring.find('"\n')
ogip = ipstring[ipstart+10:ipend-6]


working_proxy = []

print("making...")
make_proxy()
proxers = list(set(proxylist))
print("concurrent...")
with concurrent.futures.ThreadPoolExecutor() as execu:
  working_proxy = []
  execu.map(extract, proxers)
print("done...")

urls = []
this = True
event = 0
while this == True:
    receiver = "misterphil12@hotmail.com"
    url = "https://sandiego.craigslist.org/search/cta"
    counter = 0
    for proxy in working_proxy:
      try:
        cr = cloudsession
        cr.proxies = {
                 'http':proxy,
                 'https':proxy
              }
        scrape = cr.get(url).content
        work = True
        break
      except:
        counter += 1
        work = False
    print("got craigslist")
    working_proxy = working_proxy[counter:]
    soup = bs.BeautifulSoup(scrape, "lxml")
    strsoup = str(soup)
    hrefs = soup.find_all('a', class_="result-image gallery", href=True)
    for href in hrefs:
        strhref = str(href)
        start = strhref.find("href")
        end = strhref.find(".html")
        checking = strhref[start+6:end+5]
        if checking not in urls:
            urls.append(checking)
    print(urls)
    allcars = []
    counter = 0
    for i in range(event, len(urls)): 
        event += 1
        for proxy in working_proxy:
            try:
              get = cloudsession
              get.proxies = {
                   'http':proxy,
                   'https':proxy
                }
              linkscrape = get.get(urls[i]).content
              craigs = True
              break
            except:
              craigs = False  
              counter += 1
        if craigs == True:
            options = bs.BeautifulSoup(linkscrape, "lxml")
            prices = options.find_all(class_="price")
            thing = str(options)
            try:
                price = str(prices[0])[20:-7]
                price = price.replace(',', '')
                x = thing.find('VIN:')
                y = thing.find('odometer:')
                if x >= 0:
                    vin = thing[x+5:x+25]
                    vin = vin.replace("<b>", "")
                    vin = vin.replace(" ", "")
                    miles = thing[y+13:y+19]
                    miles = miles.replace("<", "")
                    miles = miles.replace(" ", "")
                    if miles.isnumeric() == True:
                        ifvin = "https://marketvalue.vinaudit.com/getmarketvalue.php?key=VA_DEMO_KEY&vin="+str(vin)+"&format=json&period=90&mileage="+str(miles)
                    else:
                        miles = 0
                        ifvin = "https://marketvalue.vinaudit.com/getmarketvalue.php?key=VA_DEMO_KEY&vin="+str(vin)+"&format=json&period=90&mileage="+str(miles)
                    allcars.append({"title":"","price": price,"vin": vin,"miles":miles,"suggested":1,"discount":1, "url": ifvin, "location": urls[i], "done": False})
                else:
                    allcars.append({"url": "", "done": True})
            except:
                allcars.append({"url": "", "done": True})
        else:
            allcars.append({"url": "", "done": True})
    print(allcars)
    working_proxy = working_proxy[counter:]
    make = False
    did = 0
    working = False
    while make == False:
        count = 0
        events = 0
        for car in allcars:
            events += 1
            if car['done'] != False:
                count += 1
        if events <= count:
            make = True
            break
        for vurl in allcars:
            if vurl['url'] != '' and vurl['done'] == False:
                for proxy in working_proxy:
                    try:
                        cloudsession.proxies = {
                           'http':proxy,
                           'https':proxy
                        }
                        cg = cloudsession.get(vurl['url'])
                        soup = str(bs.BeautifulSoup(cg.content, "lxml"))
                        start = soup.find("prices")
                        end = soup.find("below")
                        tstart = soup.find('true,')
                        tend = soup.find("vehicle")
                        did +=  1
                        vurl['title'] = soup[tstart+13: tend-4]
                        vurl['suggested'] = float(soup[start+21: end-3])
                        price = str(vurl['price'])
                        price = price.replace("$","")
                        discount = 100 - (float(price)/vurl['suggested'] * 100)
                        vurl['discount'] = discount
                        vurl['done'] = True
                        working = True
                        break
                    except:
                      working = False
        if working == True:
            make = True
            break
        proxy_list = []
        make_proxy()
        proxers = list(set(proxylist))
        with concurrent.futures.ThreadPoolExecutor() as execu:
          working_proxy = []
          execu.map(extract, proxers)
    tool = []
    for item in allcars:
        if item['url'] != "" and 10 < float(item['discount']) < 90:
            for i in item:
                if i != "done":
                    tool.append(str(i)+" - "+str(item[i]))
    string = """"""
    print(tool)
    for i in tool:
        string = string + str(i) + "\n"
    print(string)
    s = smtplib.SMTP("smtp.live.com",587)
    sender_email = "escogold@hotmail.com"
    password = os.environ['email']
    s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(sender_email, password)
    print("logged in")
    msg = email.message_from_string(string)
    s.sendmail(sender_email, receiver, msg.as_string())
    sleep(86400/24)