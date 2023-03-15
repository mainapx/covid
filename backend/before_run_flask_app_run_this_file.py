import urllib.request
import codecs
import bs4
import threading;from threading import Lock
import re,sys
import time
import MySQLdb
import random

another_opener=set();
data={}
link=set()
totalcount=0
sqlconnection=MySQLdb.connect(host="localhost",port=3306,user="root",passwd="test",db="flask_covid")
cmd=sqlconnection.cursor()

def AnotherFucker(bb):
    b=urllib.request.Request(bb);
    test.add_header("User-Agent","Mozilla/firefox Gecko");
    test.add_header("Cookie","CAKEPHP=7b968a28278bd2e6d5ab75434536fea0; _gid=GA1.3.1782744463.1624966682; _ga=GA1.3.241936881.1624966682;__gads=ID=b4430074c7f5d8b5-2260931b13ca009b:T=1624966683:RT=1624966683:S=ALNI_MbRiVMCMiPjOq7WeCKJZSwlz39i-g")

    v=bs4.BeautifulSoup(str(urllib.request.urlopen(b).read()),features="html5lib")
    bsw=v.find_all("div",class_="companyDetails")
    
    hospital_name = ""
    state_name = ""
    city_name = ""
    contact_number = ""
    address = ""

    for xr in bsw[0].find_all("p"):
        if "Name:" in str(xr):
            hospital_name=xr.text.split("  ")[1]
        if "State:" in str(xr):
            state_name=xr.text.split("  ")[1]
        if "City:" in str(xr):
            city_name=xr.text.split("  ")[1]
        if "Contact No:" in str(xr):
            contact_number=xr.text.split("   ")[1]
        if "Address" in str(xr):
            address=xr.text.split(": ")[1]

    ventilatorreserved=random.randint(0,10)
    ventilatorvaccant=random.randint(0,10)
    totalventilators=ventilatorreserved+ventilatorvaccant
    vaccantbeds=random.randint(0,1000)
    reservedbeds=random.randint(0,1000)
    totalbeds=vaccantbeds+reservedbeds
    
    data['Name']=hospital_name
    data['State']=state_name
    data['City']=city_name
    data['Telephone']=contact_number
    data['VentilatorsReserved']=ventilatorreserved
    data['VentilatorsVaccant']=ventilatorvaccant
    data['TotalVentilators']=totalventilators
    data['Vacantbeds']=vaccantbeds
    data['Reservedbeds']=reservedbeds
    data['Location']=city_name
    data['Totalbeds']=totalbeds
    cmd.execute("INSERT INTO hospital(Name,Reservedbads,Vacantbads,Ventilatorsreserved,Ventilatorvacant,State,City,Telephone,Totalbeds,TotalVentilators,Location)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (data['Name'].replace("'",""),data['Reservedbeds'],data['Vacantbeds'],data['VentilatorsReserved'],data['VentilatorsVaccant'],data['State'],data['City'],str(data['Telephone']),data['Totalbeds'],data['TotalVentilators'],data['Location']))
    sqlconnection.commit()
    sys.stdout.write("Collecting Database Please wait ...\t\r%s/Unknown" % "...")


def Requester(requesthandler):
    bm=urllib.request.Request(requesthandler);
    test.add_header("User-Agent","Mozilla/firefox Gecko")
    reader=str(urllib.request.urlopen(bm).read())
    v=bs4.BeautifulSoup(reader,features="html5lib")
    collector=v.find_all("div",class_="row addressWrap mt-2")
    for x in collector:
        for xw in x.select("a[href]"):
            try:
                another_opener.add(xw).get("href")
            except:
                pass

    for y in another_opener:
        AnotherFucker(y.get("href"))


links=set()
lst=[]
test=urllib.request.Request("https://pin-code.org.in/hospitals/listing")
test.add_header("User-Agent","Mozilla/firefox Gecko")
try:
    test1=urllib.request.urlopen(test)
except urllib.error.HTTPError as e:
    pass

bs=bs4.BeautifulSoup(test1,features="html5lib")
result=bs.find_all("ul",class_="list1 row mt-3")[0]
h=result.find_all("li")
for x in h:
    link.add(x.find("a").get("href"))
for x in link:
    Requester(x)
    import time



"""def Threader(ptag,tracker):
    if tracker is None:
        myrequest=urllib.request.Request("https:%s" % (ptag.attrs['href']))
    else:
        myrequest=urllib.request.Request("https://www.google.com/search?q=%s" % (tracker))
    myrequest.add_header('User-Agent','Mozilla/firefox')
    try:
        b=urllib.request.urlopen(myrequest).read()
        bv=bs4.BeautifulSoup(b.decode(encoding="latin"),features="html5lib")
        return bv
    except Exception as bs:
        pass

def myfunction():
    counter,secondcounter=0,0
    for x in h:
        testing=x.find_all("td")
        for p in testing:
            if p.find("a",attrs={"itemprop":"url"}):
                url_handler=p.find("a",attrs={'itemprop':'url'})

                mobilephone=Threader(url_handler,None).find("dd",attrs={'itemprop':'telephone'}).text.replace("\n","")
                

            elif p.find("a",href=re.compile(".*state.*",re.IGNORECASE)):
                data['State']=p.text
            elif p.find("a",href=re.compile(".*city.*",re.IGNORECASE)):
                data['City']=p.text
            else:
                pass
            try:
                final_text=p.text.replace(" ","+")
                resp_handler=Threader(None,"%s+langitude+altitude" % (final_text)).find("div",class_="BNeawe iBp4i AP7Wnd").text
                data['Location']=resp_handler
            except:
                continue
            secondcounter+=1
        sys.stdout.write("Collecting Database Please wait ...\t\r%s/1348" % counter)
        sys.stdout.flush()
        counter+=1
        try:
        except Exception as b:
            pass
"""
