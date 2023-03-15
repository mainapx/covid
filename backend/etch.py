import urllib.request,MySQLdb,bs4,re,sys,threading,schedule,urllib.parse,codecs,datetime,ast,json
counter=0
new_query=[]
class GetCovidCase:
    def __init__(self):
        self.sqlconnection=MySQLdb.connect(host="localhost",port=3306,user="root",password="",db="flask_covid")
        self.cursortesting=self.sqlconnection.cursor()

    def Fetcher(self,x):
        self.connect=urllib.request.Request(x)
        self.connect.add_header('User-Agent','Mozilla/firefox Gecko Window NT')
        self.testing=urllib.request.urlopen(self.connect)
        self.mybs4=bs4.BeautifulSoup(str(self.testing.read()),features="html5lib")
        state_name=self.testing.geturl().split("+")[3].split("&")[0]
        try:
            js_tag=self.mybs4.find_all("script")
            first_json=str(js_tag).find("trendData")
            last_json=str(js_tag).find("; try")
            final_json=str(js_tag)[first_json:last_json].replace("trendData =","")
            api_json=json.loads(final_json)
            for x in api_json:
                previous_time=str(datetime.datetime.fromtimestamp(int(x['t'])/1000)).split(" ")[0]
                self.cursortesting.execute("INSERT INTO history(State,ConfirmCases,TimeStamp,Deaths,Recovered,Vaccinated)VALUES('%s','%s','%s','%s','%s','%s');" % (state_name,x['c'],previous_time,x['d'],x['r'],x['v']))
                self.sqlconnection.commit()
            if re.findall("q=.*statistics.*",str(self.testing.geturl())):
                current_checker=self.mybs4.find_all("div",class_="c_chgVal b_footnote")
                myfinder=self.mybs4.find_all("div",class_="cov_breakdown")
                for m in myfinder:
                    nested_find=m.find_all("div",class_="cov_row")
                    for x in nested_find[1:]:
                        n=x.find_all("div",class_="cov_cell")
                        self.cursortesting.execute("INSERT INTO cases(State,TotalCase,Deaths,Recovered,TodayCases,Locality,TodayDeath,TodayRecovered,Cordinates) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (state_name,n[1].string,n[2].string,n[3].string,current_checker[0].string,n[0].string,current_checker[1].string,current_checker[2].string,''))
                        self.sqlconnection.commit()
            elif re.findall("India.*",self.testing.geturl(),re.IGNORECASE):
                IndiaCase=[]
                total_handler=self.mybs4.find("div",class_="c_stat c_cnfrm").find("div",class_="c_row")
                indiatodaycase=total_handler.find("div",class_="c_chgVal b_footnote").string
                indiatotalcase=total_handler.find("div",class_="c_cnt b_focusTextExtraSmall").string

                death_handler=self.mybs4.find("div",class_="c_stat c_dths").find("div",class_="c_row")
                todaydeath=death_handler.find("div",class_="c_chgVal b_footnote").string
                totaldeath=death_handler.find("div",class_="c_cnt b_focusTextExtraSmall").string

                recovered_handler=self.mybs4.find("div",class_="c_stat c_rcvrd").find("div",class_="c_row")
                todayrecovered=recovered_handler.find("div",class_="c_chgVal b_footnote").string
                totalrecovered=recovered_handler.find("div",class_="c_cnt b_focusTextExtraSmall").string
                self.cursortesting.execute("INSERT INTO cases(State,TotalCase,Deaths,Recovered,TodayCases,Locality,TodayDeath,TodayRecovered,Cordinates) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (state_name,indiatotalcase,totaldeath,totalrecovered,indiatodaycase,state_name,todaydeath,todayrecovered,0))

            else:
                my_data=self.mybs4.find("a",href=re.compile("^/search.*FORM=COVIDR$"),string=re.compile("see.*",re.IGNORECASE)).get('href')
                if re.findall(".*India.*",(my_data)):
                    totalcasecheck=self.mybs4.find_all("div",class_="cov_cases")
                    first_list=totalcasecheck[0].find_all("div",class_="c_cnt b_focusTextExtraSmall")
                    second_list=totalcasecheck[0].find_all("div",class_="c_chgVal b_footnote")
        
                    total_state_case=first_list[0].string
                    total_death_case=first_list[1].string
                    total_recovered=first_list[2].string
                   
                    today_case=second_list[0].string    
                    today_death=second_list[1].string
                    today_recovered=second_list[2].string
                    self.cursortesting.execute("INSERT INTO cases(State,TotalCase,Deaths,Recovered,TodayCases,Locality,TodayDeath,TodayRecovered,Cordinates) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (state_name,total_state_case,total_death_case,total_recovered,today_case,state_name,today_death,today_recovered,''))
                    self.sqlconnection.commit()
                else:
                    self.Fetcher("https://bing.com%s" % (my_data))
        except Exception as e:
            pass
        global counter
        sys.stdout.write("%s%s Processing\r" % (counter,'%'))
        counter+=1

if __name__ == "__main__":
    mac_list=set()
    states=['india','arunachal+pradesh','delhi','uttar+pradesh','assam','goa','orissa','haryana','himachal+pradesh','tamil+nadu','bihar'
        'chhattisgarh','gujrat','jharkhand','karnataka','kerala','madhya+pradesh','maharashtra','manipur','meghalaya','mizoram','nagaland','punjab','sikkim',
        'telangana','tripura','uttarakhand','west+bengal','andaman+and+nicobar+islands','ladakh']

    def Repeater():
        print("[*] Parsing Corona Cases...")
        be=GetCovidCase()
        for x in states:
            paramvalue='https://www.bing.com/search?q=coronavirus'+'+'+'cases'+ '+'+'in'+ '+'+'%s' % (x)
            b=threading.Thread(target=be.Fetcher,args=(paramvalue,))
            b.daemon=True
            b.start()
            b.join()
        be.cursortesting.execute("SELECT Locality FROM cases");
        user_data=be.cursortesting.fetchall()
        for x in user_data:
            if " " in x[0]:
                y=x[0].replace(" ","+")
            else:
                y=x[0]
            b=urllib.request.Request("https://www.google.com/search?q=" + 'longitude' + '+' + 'and' + '+' + 'latitude' + '+' + 'of' + '+' + y)
            b.add_header('User-Agent','Mozilla/firefox Gecko Window NT')
            super_test=urllib.request.urlopen(b).read()
            h=bs4.BeautifulSoup(str(super_test),features="html5lib")
            try:
                cordinate=urllib.parse.unquote(h.find("div",class_="BNeawe iBp4i AP7Wnd").string)
                be.cursortesting.execute("UPDATE  cases SET Cordinates='%s' WHERE Locality='%s';" % (str(cordinate),x[0]))
                be.sqlconnection.commit()
            except Exception as  e:
                pass
            global counter
            sys.stdout.write("%s%s of %s Just wait few Time...\r" % (counter,'%',len(user_data)-counter))
            counter+=1
        be.cursortesting.execute("UPDATE cases SET Cordinates=REPLACE(Cordinates,'xb0','°');")
        be.sqlconnection.commit()
    schedule.every().day.at("23:50").do(Repeater)
    #while True:
    #    schedule.run_pending()
