import urllib.request
import json
import ssl
import datetime
import bs4
import re

covidupdate=[]
NOT_FOUND={}

class CovidTracker:
    def __init__(self,**kwargs):
        self.statewise=kwargs['state']
        self.indiawise=kwargs['india']
        self.active=kwargs['activecase']
        self.todaydate=datetime.date.today()
             
    def SSLHandler(self):
        a=ssl.create_default_context()
        a.check_hostname=False
        a.verify_mode=ssl.CERT_NONE
        return a

    def parameterhandler(self,urltarget):
        n=urllib.request.Request(urltarget)
        n.add_header("User-Agent",'Mozilla/firefox Gecko 8. Window NT')
        c=urllib.request.urlopen(n,context=self.SSLHandler())
        return c

    def Connection(self):                
        if  self.statewise  == None:
            a=self.parameterhandler(self.indiawise).read()
            b=bs4.BeautifulSoup(a,features="html5lib")

            totalcase=b.find("div",class_=re.compile("^number-table-main")).string   # finding in worldomter web
            totaldeath=b.find("span",class_=re.compile("^number-table"),string=re.compile('^\d')).string
    
            activecase=self.parameterhandler(self.active).read()
            act=b.select("span[style='color:#aaa']")
            activepeople=re.findall(">.*\d",str(act))[0].replace(">","")
            IndiaUpdate={}
            IndiaUpdate['TotalCase']=totalcase
            IndiaUpdate['ActiveCase']=activepeople
            IndiaUpdate['Deceased']=totaldeath
            covidupdate.append(IndiaUpdate)
            print(covidupdate)
        else:
            COUNTER=0,
            integer_new_case=None,
            new_state_case=None
            a=self.parameterhandler(self.statewise).read()
            b=bs4.BeautifulSoup(a,features="html5lib")
            mainsite=b.find("a",href=re.compile("https.*indiatoday.in.*")).attrs['href']
            deeperinside=self.parameterhandler(mainsite)
            c=bs4.BeautifulSoup(deeperinside,features="html5lib")

            Main_Title=c.find_all("div",class_="timeline")
            for x in Main_Title:
                delhicase=x.find("p",string=re.compile("Delhi [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                maharastracase=x.find("p",string=re.compile("maharastra [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                sikkim=x.find("p",string=re.compile("sikkim [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                arunachalpardesh=x.find("p",string=re.compile("arunachal pardesh [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                biharcase=x.find("p",string=re.compile("bihar [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                jharkhandcase=x.find("p",string=re.compile("jharkhand [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                himachalcase=x.find("p",string=re.compile("HP|himachal pardesh [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                gujratcase=x.find("p",string=re.compile("gujrat [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                haryanacase=x.find("p",string=re.compile("haryana [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                goacase=x.find("p",string=re.compile("goa [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                andhrapardeshcase=x.find("p",string=re.compile("andhra pardesh|A.P|AP [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                chattisgarhcase=x.find("p",string=re.compile("chattisgarh [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                uttarpadeshcase=x.find("p",string=re.compile("uttar pardesh|U.P|UP [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                rajesthancase=x.find("p",string=re.compile("rajesthan [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                westbangalcase=x.find("p",string=re.compile("west bangal [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                nagalandcase=x.find("p",string=re.compile("nagaland [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                punjabcase=x.find("p",string=re.compile("punjab [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                odishacase=x.find("p",string=re.compile("odisha [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                chennaicase=x.find("p",string=re.compile("chennai [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                mizoramcase=x.find("p",string=re.compile("mizoram [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                manipurcase=x.find("p",string=re.compile("manipur [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                tamilnaducase=x.find("p",string=re.compile("tamil nadu|T.N|TN [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                uttrakhandcase=x.find("p",string=re.compile("uttrakhand [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                meghalayacase=x.find("p",string=re.compile("meghalaya [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                madhyapardeshcase=x.find("p",string=re.compile("MP|M.P|madhya pardesh [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                tripuracase=x.find("p",string=re.compile("tripura [New|new] [Reported|reported|Report|report]",re.IGNORECASE))
                assamcase=x.find("p",string=re.compile("assam [New|new] [Reported|reported|Report|report]",re.IGNORECASE))

                NOT_FOUND['delhi']=delhicase
                NOT_FOUND['maharastra']=maharastracase
                NOT_FOUND['gujrat']=gujratcase
                NOT_FOUND['uttarpadeshcase']=uttarpadeshcase
                NOT_FOUND['andrapardesh']=andhrapardeshcase
                NOT_FOUND['chattisgarh']=chattisgarhcase
                NOT_FOUND['tamilnadu']=tamilnaducase
                NOT_FOUND['meghalaya']=meghalayacase
                NOT_FOUND['madhyapardesh']=madhyapardeshcase
                NOT_FOUND['chennai']=chennaicase
                NOT_FOUND['uttrakhand']=uttrakhandcase
                NOT_FOUND['rajesthan']=rajesthancase
                NOT_FOUND['manipur']=manipurcase
                NOT_FOUND['tripura']=tripuracase
                NOT_FOUND['assam']=assamcase
                NOT_FOUND['punjab']=punjabcase
                NOT_FOUND['westbangal']=westbangalcase
                NOT_FOUND['mizoram']=mizoramcase
                NOT_FOUND['himachal']=himachalcase
                NOT_FOUND['haryana']=haryanacase
                NOT_FOUND['goa']=goacase
                NOT_FOUND['chattisgarh']=chattisgarhcase
                NOT_FOUND['bihar']=biharcase
                NOT_FOUND['jharkhand']=jharkhandcase
                NOT_FOUND['odisha']=odishacase
                NOT_FOUND['arunachal']=arunachalpardesh
                NOT_FOUND['sikkim']=sikkim
                NOT_FOUND['nagaland']=nagalandcase

        statename=[]
        for x in NOT_FOUND:
            if NOT_FOUND[x]==None:
                nestedbs4=bs4.BeautifulSoup(self.parameterhandler(PREFER_QUERY[1]),feature='html5lib')
                nest_href=nestedbs4.find("a",href=re.compile("^[https].*financialexpress.com.*")).attrs['href']
                nest_href=self.parameterhandler(nest_href)
                nest_beaut=bs4.BeautifulSoup(nest_href,features="html5lib")
                M=nest_beaut.find_all("div",class_="body-lvblg")
                my_string=NOT_FOUND[x].split(" ")[0]
                state_name=mystring
                global append_list

                for b in M:
                    b=re.sub(".*[24 hourse|24 Hours|24hours]","",b)[0]
                    if ("new" or "recovery" or "death")  in b:
                        if "ANI" in b:
                            ani_spliter=b.split(".")
                            for x in ani_spliter[0]:
                                first_anit=x.split()
                                for pi in first_anit:
                                    pi=str(pi).replace(",","")
                                    if re.findall("new case| new positive.*",re.IGNORECASE,pi):       
                                        if pi.isdigit():
                                            statename['Newcase']=pi
                                
                            active_case=re.findall("active case.*\d+",re.IGNORECASE,ani_spliter[1])
                            total_positive_case=re.findall("total|postive.*\d+",re.IGNORECASE,ani_spliter[1])

                            for AC_Case in active_case.split():
                                if AC_Case.isdigit():
                                    statename['Activecase']=AC_Case
                            for Total_pc in active_case.split():
                                if Total_pc.isdigit():
                                    statename['Totalcase']=Total_pc

                        """
                        todayrecover=b.string.split(" ")
                        for bc in newcase_positive_death:
                            if bc.isdigit():
                                currentindex=b.index(bc)
                                if re.findall("cases|New|reports|positive",b[:currentindex]):
                                    first_spliter=re.findall("cases|New|reports|positive",b[:currentindex])
                                    for x in first_spliter:
                                        if x.isdigit():
                                            todaycoronacase=bc
                                else:
                                    second_spliter=re.findall("New|cases",b[currentindex:b.index(",")])
                                    for u in second_spliter:
                                        if u.isdigit():
                                            todaycoronacase=bc
                        """
                        b=b.replace("24|hours.*","")
                        append_list=[]
                        today_case=b.split(", ")
                        for h_l in today_case:
                            replacer=h_l.find("and") or h_l.find("And")
                            if replacer:
                                append_list=h_l.split(h_l[replacer])
                            append_list.append(h_l)

                        for x in append_list:
                            if re.findall("reports|new|cases",re.IGNORECASE,x):
                                N_c=re.findall("reports|new|cases",re.IGNORECASE,x)
                                for o_p in N_c:
                                    if x.isdigit():
                                        integer_new_case=o_p
                            elif re.findall("death|Deceased|deaths",re.IGNORECASE,x):
                                N_d=re.findall("death|Deceased|deaths",re.IGNORECASE,x)
                                for o_l in N_d:
                                    if o_l.isdigit():
                                        integer_death_case=o_l
                            else:
                                R_p=re.findall("recover|recoveries|",re.IGNORECASE,x)
                                if R_p:
                                    for X_l in R_p:
                                        if X_l.isdigit():
                                            integer_recover_case=X_l
                    else:
                        b=b.replace(",","")
                        if re.findall("Total.*\d+",b):
                            total_positive_case=re.findall("Total.*\d+",re.IGNORECASE,b)[0].split()
                            active_case=re.findall("Active.*\d",re.IGNORECASE,b)[0].split()
                            for second_tag in total_positive_case:
                                if second_tag.isdigit():
                                    mydict={}
                                    mydict[""]
                                    statename[statename]

                    #M.find("p",string=re.compile("%s.*cases \d.*" % (mystring),re.IGNORECASE),M)

if __name__ == "__main__":
    m=CovidTracker(state=None,india="https://www.worldometers.info/coronavirus/country/india",activecase="https://covid19.who.int/region/searo/country/in")
    m.Connection()
    
    PREFER_QUERY=['corona+update+in+delhi+in+last+24+hours','corona+update+in+maharastra']
    #for p in states:
    n=CovidTracker(state="https://www.bing.com/search?q=%s" % (PREFER_QUERY[0]),india=None,activecase=None)
    n.Connection()
