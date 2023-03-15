import flask,os,sys,flask_cors;from flask_cors import CORS
import ariadne;from uuid import uuid1;import random;import hashlib;import time
import urllib.parse;import socketio;from werkzeug.routing import BaseConverter
from flask import Flask, send_from_directory
from flask_session import Session
from SmtpHandler import SMTPSender;import MySQLdb;import re;import json;from flask import *

OTP_Value={}
class RegularExpression(BaseConverter):
	def __init__(self,map,*args):
		self.map=map
		self.regex=args[0]

class SqlApi:
	def __init__(self):
		try:
			self.sqlconnection=MySQLdb.connect(host="localhost",port=3306,user="root",password="test",db="flask_covid")

			self.cmdcursor=self.sqlconnection.cursor()
		except MySQLdb._exceptions.OperationalError as m:
			print(m)
			#print("Cannot Connect To Mysql server...")
			sys.exit(1)

	def SqlQuery(self,typecheck,authorizedid,otp,firstname,lastname,phone,address,username,password):
		if typecheck.startswith("login"):
			LOGIN_QUERY="SELECT * FROM login WHERE Username='%s' AND password='%s';" % (username,password)
			return self.cmdcursor.execute(LOGIN_QUERY)

		elif typecheck.startswith("register"):
			queryregister=("INSERT INTO register(Firstname,Lastname,Phone,Address,Username,Password,UID) VALUES('%s','%s','%s','%s','%s','%s','%s');" % (firstname,lastname,phone,address,username,password,authorizedid),
				"INSERT INTO login(Username,Password,UID,Firstname,Lastname,Phone,verified) VALUES('%s','%s','%s','%s','%s','%s',0);" % (username,password,authorizedid,firstname,lastname,phone))
			for x in queryregister:	
				self.cmdcursor.execute(x)
				self.sqlconnection.commit()
		elif typecheck.startswith("Verify"):
			check_otp="SELECT * FROM register WHERE UID='%s' AND Username='%s';" % (authorizedid,username)
			return self.cmdcursor.execute(check_otp)				
		elif typecheck.startswith('sendotp'):
			executer_otp="SELECT Username from login WHERE UID='%s';" % authorizedid
			return self.cmdcursor.execute(executer_otp)
		elif typecheck.startswith("hospitalnames"):
			hospital_details="SELECT * FROM login WHERE UID='%s' AND Username='%s';" % (authorizedid,username)
			return self.cmdcursor.execute(hospital_details)
		
		elif typecheck.startswith("accountupdate"):
			q1="UPDATE  register SET Firstname='%s',Password='%s',Phone='%s',Lastname='%s',Username='%s' WHERE UID='%s';" % (firstname,password,phone,lastname,username,authorizedid)
			q2="UPDATE  login SET Firstname='%s',Password='%s',Phone='%s',Username='%s',Lastname='%s' WHERE UID='%s';" % (firstname,password,phone,username,lastname,authorizedid)

			if self.cmdcursor.execute(q1) and self.cmdcursor.execute(q2):
		 		return "ok"
			else:
		 		return "no"
			
		elif typecheck.startswith("deleteaccount"):
			delete_query="DELETE FROM login,register USING login,register WHERE register.UID=login.UID AND register.UID='%s';" % (authorizedid)
			self.cmdcursor.execute(delete_query)
			if self.sqlconnection.commit():
				return True
			else:
				return False
		elif typecheck.startswith("getadminaccount"):
			testing="SELECT Username,Password,UID,Role FROM admin;"
			if self.cmdcursor.execute("SELECT * FROM admin WHERE UID='%s' AND Role='Admin';" % (authorizedid)) == 1:
				return self.cmdcursor.execute(testing)


		elif typecheck.startswith("getdatabase"):
			admin_db_fetch="SELECT * FROM hospital;"
			self.cmdcursor.execute(admin_db_fetch)

		elif typecheck.startswith("getdetail"):
			detail_query="SELECT * FROM register WHERE UID='%s';" % authorizedid
			self.cmdcursor.execute(detail_query)

		elif typecheck.startswith("adminlogin"):
			admin_login="SELECT * FROM admin WHERE Username='%s' AND Password='%s';" % (username,password) 
			self.cmdcursor.execute(admin_login)
		elif typecheck.startswith("feedback"):
			feedback_user="UPDATE feedback SET message='%s' WHERE Token='%s' AND Username='%s';" % (address,authorizedid,username)
			self.cmdcursor.execute(feedback_user)
			self.sqlconnection.commit()
		elif typecheck.startswith("bookhospital"):
			send_hospital_status="SELECT UID  FROM login WHERE EXISTS(SELECT * FROM register WHERE UID='%s');" % (authorizedid)
			if self.cmdcursor.execute(send_hospital_status) == 1:
				query_result="UPDATE booking SET Patientrequest='%s',Patientusername='%s',Patientname='%s',Patientcontact='%s' WHERE EXISTS(SELECT * FROM register WHERE UID='%s');" % ('1',username,firstname,phone,authorizedid)
				return self.cmdcursor.execute(query_result)
		else:
			HOSPITAL_QUERY=("SELECT * FROM register WHERE Username='%s',Password='%s';" % (username,password))
	def ApiAuthentication(self,**kwargs):
		if kwargs['method']=="login":
			user_name=re.findall(".*@.*[.com|.org|.in|.co.uk]$",kwargs['user'])
			if not user_name:
				errorresponse=make_response(json.dumps({'status':'Failed','message':'Invalid Email Please Enter Corrent Emailid'}),400)
				errorresponse.headers['Content-Type']="application/json"
				return errorresponse
			elif kwargs['passwd'] == '':
				passworderror=make_response(json.dumps({'status':'Failed','message':'Please Enter Password Minimum 8 digits'}),400)
				passwroderror.headers['Content-Type']="application/json"
				return passworderror
			else:
				self.SqlQuery("login",None,None,None,None,None,None,kwargs['user'],kwargs['passwd'])
				try:
					result=self.cmdcursor.fetchall()[0]
					if len(result) > 0:
						mydict={}
						mydict['Firstname']=result[3]
						mydict['Lastname']=result[4]
						mydict['uid']=result[1]
						mydict['Username']=result[0]
						mydict['Phone']=result[5]
						successresponse=make_response(json.dumps({'status':'ok','message':'success','details':[mydict]}))
						successresponse.headers['Content-Type']="application/json"
						session['secret_session']=result[1]
						return successresponse
				except:
					errorlogin=make_response(json.dumps({'status':'Failed','message':'Invalid Authentication'}),401)
					errorlogin.headers['Content-Type']="application/json"
					return errorlogin
		elif kwargs['method'] == "register":
			filter_list=['@','.com','.in','.uk','.org','.in']
			prevention_list=(";","'",'*',")","(","]","[","-","+","/","&","$","#","!","~","`","^","%","|")
			errorvalues=[]
			for x in kwargs.values():
				if len(re.findall("<|>|script|img|<a|div",x.strip())) is not int(0):
					errorvalues.append(x)
			if errorvalues:
				errorregister=make_response(json.dumps({'status':'Failed','message':'Special Characters are not allowed in %s' % (errorvalues)}),400)
				errorregister.headers['Content-Type']="application/json"
				errorvalues.clear()
				return errorregister

			elif [x in kwargs['username'] for x in filter_list] and [x not in kwargs['username'] for x in prevention_list] and (kwargs['firstname'] and  kwargs['lastname'] and  kwargs['phone'] and  kwargs['address'] and  kwargs['password']) !="":
				checkifexists=self.cmdcursor.execute("SELECT * FROM register WHERE Username='%s' AND Password ='%s';" % (kwargs['username'],kwargs['password']))
				try:
					registerfetcher=self.cmdcursor.fetchall()
					if len(registerfetcher[0]):
						already_exists=make_response(json.dumps({'status':'Failed','message':'Account Already exists'}),400)
						already_exists.headers['Content-Type']="application/json"
						return already_exists
				except Exception as b:
					idgen=hashlib.new('sha256')
					idgen.update(str(uuid1()).encode(encoding="utf-8"))
					authorizedid=idgen.hexdigest()
					session['secret_session'] =authorizedid
					self.SqlQuery("register",authorizedid,None,kwargs['firstname'],kwargs['lastname'],kwargs['phone'],kwargs['address'],kwargs['username'],kwargs['password'])
					b=make_response(json.dumps({'status':'success','message':'Account Created','email':kwargs['username'],'Firstname':kwargs['firstname'],'Lastname':kwargs['lastname'],'uid':authorizedid}),200)
					b.headers['Content-Type']="application/json"
					return b
			else:
				b=make_response({'status':'Failed','message':'Something is Wrong Please Try again'},429)
				b.headers['Content-Type']='application/json'
				return b
		elif kwargs['method']=='Verify':
			self.SqlQuery("Verify",kwargs['UID'],kwargs['otp'],None,None,None,None,kwargs['checkemail'],None)
			print(session)
			try:
				if len(self.cmdcursor.fetchall()) and (OTP_Value[kwargs['checkemail']]==kwargs['otp']):
					self.cmdcursor.execute("UPDATE TABLE login SET Verified='1' WHERE UID='%s';" % kwargs['UID'])
			except:
				c=make_response(json.dumps({"status":"Failed","message":"Invalid OTP"}),200)
				c.headers['Content-Type']='application/json'
				return c
			b=make_response(json.dumps({"status":"success","message":"verified"}),200)
			b.headers['Content-Type']='application/json'
			return b
		elif kwargs['method']=='sendotp':
			self.SqlQuery("sendotp",kwargs['authorization'],None,None,None,None,None,kwargs['emailuser'],None)
			try:
				dataresult=self.cmdcursor.fetchall()[0]
				if len(dataresult) is not int(0):
					randotp=random.randint(10000,99000)
					OTP_Value[dataresult[0]]=randotp
					smtpobj=SMTPSender(dataresult[0],randotp)
					return smtpobj.Sender()
			except Exception as b:
				pass
			b=make_response(json.dumps({'status':'Failed','message':'Unauthorized'}),401)
			b.headers['Content-Type']='application/json'
			return b
		elif kwargs['method'] == "hospitalnames":
			self.SqlQuery("hospitalnames",kwargs['authorization'],None,None,None,None,None,kwargs['email'],None)
			try:
				datahospital=self.cmdcursor.fetchall()[0]

				if datahospital:
					self.cmdcursor=self.sqlconnection.cursor(MySQLdb.cursors.DictCursor)
					self.cmdcursor.execute("SELECT * FROM hospital")
					fetcher=self.cmdcursor.fetchall()
					testlist=[]
					for p in fetcher:
						testlist.append(p)
					if len(fetcher):
						c=make_response(json.dumps({"status":"success","Hospitals":testlist}),200)
						c.headers['Content-Type']='application/json'
						return c
			except Exception as e:
				print(e)
				pass
			c=make_response(json.dumps({"status":"Failed","message":"No Hospitals Found"}),400)
			c.headers['Content-Type']='application/json'
			return c
		
				
		elif kwargs['method'] == "accountupdate":
			if self.SqlQuery("accountupdate",kwargs['authorization'],None,kwargs['firstname'],kwargs['lastname'],kwargs['phone'],None,kwargs['emailid'],kwargs['password']) == "ok":
				myresponse=make_response(json.dumps({'status':"ok",'message':'Account Updated'}),200)
				myresponse.headers['Content-Type']="application/json"
				return myresponse
			else:
				g=make_response(json.dumps({'status':'Failed','message':'Unauthorized'}),401)
				g.headers['Content-Type']='application/json'
				return g
		
		elif kwargs['method'] == "deleteaccount":
			if self.SqlQuery("deleteaccount",kwargs['authorization'],None,None,None,None,None,kwargs['username'],kwargs['password']) ==True:
				pass
			else:
				v=make_response(json.dumps({'status':'Failed','message':'Something is Wrong to delete account'}),429)
				v.headers['Content-Type']='application/json'
				return v					
			g=make_response(json.dumps({'status':'ok','message':'Account Deleted'}),200)
			g.headers['Content-Type']='application/json'
			return g
		elif kwargs['method']=='getdetail':
			self.SqlQuery("getdetail",kwargs['authorization'],None,None,None,None,None,None,None)
			result_set=self.cmdcursor.fetchall()[0]
			try:
				if len(result_set):
					user_object={}
					user_object['Firstname']=result_set[0]
					user_object['Lastname']=result_set[1]
					user_object['Phone']=result_set[2]
					user_object['Password']=result_set[4]
					user_object['Emailid']=result_set[6]
					h=make_response(json.dumps({'status':'ok','message':'success','details':[user_object]}),200)
					h.headers['Content-Type']='application/json'
					return h
			except Exception as e:
				pass
			b=make_response(json.dumps({'status':'Failed','message':'Unauthorized'}),401)
			b.headers['Content-Type']='application/json'
			return b

		elif kwargs['method']=='adminlogin':
			self.SqlQuery("adminlogin",None,None,None,None,None,None,kwargs['username'],kwargs['password'])
			try:
				authorized_admin=self.cmdcursor.fetchall()[0]
				if len(authorized_admin) > 0:
					user_a={}
					print(authorized_admin)
					user_a['Phone']=authorized_admin[2]
					user_a['Emailid']=authorized_admin[6]
					user_a['authorization']=authorized_admin[5]
					session['secret_session']=authorized_admin[5]
					c=make_response(json.dumps({'status':'ok','message':'success','details':[user_a]}))
					return c
			except:
				c=make_response(json.dumps({'status':'Failed','message':'Unauthorized'}),401)
				c.headers['Content-Type']='application/json'
				return c
		elif kwargs['method'] == "getdatabase":
			self.SqlQuery("getdatabase",kwargs['authorization'],None,None,None,None,None,kwargs['email'],None)
			db_result=self.cmdcursor.fetchall()
			mylist=[]
			for x in db_result:
				user_result={}
				user_result['Hospitalname']=x[0]
				user_result['Reservebeds']=x[1]
				user_result['Vacantbeds']=x[2]
				user_result['Ventilatorreserved']=x[3]
				user_result['Ventilatorvaccant']=x[4]
				user_result['State']=x[5]
				user_result['City']=x[6]
				user_result['Telephone']=x[7]
				user_result['Totalbeds']=x[8]
				user_result['Totalventilators']=x[9]
				user_result['Sn']=x[10]
				mylist.append(user_result)
			c=make_response(json.dumps({'status':'ok','message':'success','data':mylist}),200)
			c.headers['Content-Type']='application/json'
			return c
		elif kwargs['method'] == "getadminaccount":
			self.SqlQuery("getadminaccount",kwargs['authorization'],None,None,None,None,None,kwargs['emailid'],None)
			myLst=['Username','Password','Token','Role']
			try:
				db_handler=self.cmdcursor.fetchall()[0]
				testDict={}
				for x,y in zip(db_handler,myLst):
					testDict[y]=x
			except:
				b=make_response(json.dumps({'status':"Failed",'message':'Unauthorized'}),401)
				b.headers['Content-Type']='application/json'
				return b
			print([testDict])
			b=make_response(json.dumps({'status':'ok','message':'success','data':[testDict]}),200)
			b.headers['Content-Type']='application/json'
			return b
		elif kwargs['method'] == 'getcases':
			test_send=[]
			self.cmdcursor.execute("SELECT * FROM cases WHERE Cordinates !='';")
			fetcherdata=self.cmdcursor.fetchall()
			for x in fetcherdata:
				send_dict_data={}
				send_dict_data['State']=x[0]
				send_dict_data['TotalCase']=x[1]
				send_dict_data['Deaths']=x[2]
				send_dict_data['Recovered']=x[3]
				send_dict_data['TodayCases']=x[4]
				send_dict_data['Locality']=x[5]
				send_dict_data['TodayDeath']=x[6]
				send_dict_data['TodayRecovered']=x[7]
				send_dict_data['Cordinates']=x[8]
				test_send.append(send_dict_data)
			self.cmdcursor.execute("SELECT TotalCase,Deaths,Recovered,State,TodayCases,TodayRecovered,TodayDeath FROM cases WHERE Cordinates != '0';")
			check_india_status={}
			b=self.cmdcursor.fetchall()
			lst=['TotalCases','TotalDeaths','TotalRecoverd','Country','TodayCases','TodayRecovered','TodayDeath']
			for x,y in zip(lst,b[0]):
				check_india_status[x]=y

			b=make_response(json.dumps({'status':'ok','message':'success','data':test_send,'IndiaStatus':check_india_status}),200)
			b.headers['Content-Type']='application/json'
			return b
		elif kwargs['method']=='getgraph':
			self.cmdcursor.execute("SELECT * FROM history;")
			cmd_check=self.cmdcursor.fetchall()
			my_graph=[]
			for x in cmd_check:
				mydict={}
				mydict['State']=x[0]
				mydict['TimeStamp']=x[1]
				mydict['Deaths']=x[2]
				mydict['Recovered']=x[3]
				mydict['Vaccinated']=x[4]
				mydict['ConfirmCases']=x[5]
				my_graph.append(mydict)
			v=make_response(json.dumps({'status':'ok','message':'success','data':my_graph}),200)
			v.headers['Content-Type']='application/json'
			return v
		elif kwargs['method'] == "feedback":
			self.SqlQuery("feedback",kwargs['authorization'],None,None,None,None,kwargs['address'],kwargs['emailid'],None)
			c=make_response(json.dumps({'status':'ok','message':'Your Feedback Has been Submitted'}),200)
			c.headers['Content-Type']='application/json'
			return c
		elif kwargs['method'] == "bookhospital":
			if self.SqlQuery("bookhospital",kwargs['authorization'],None,kwargs['firstname'],kwargs['lastname'],kwargs['phone'],None,kwargs['emailid'],None) == 1:
				self.sqlconnection.commit()
				b=make_response(json.dumps({'status':'ok','message':'You have successfully Applied'}),200)
				b.headers['Content-Type']='application/json'
				return b
			else:
				pass
			c=make_response(json.dumps({'status':'Failed','message':'Unauthorized'}),401)
			c.headers['Content-Type']='application/json'
			return c
		else:
			pass
class MainServer(SqlApi):
	def __init__(self):
		SqlApi.__init__(self)
		
	handler=Flask(__name__,static_folder='static')
	handler.config['SECRET_KEY']=os.urandom(16)

	# session configuration

	handler.config["SESSION_PERMANENT"] = False
	handler.config["SESSION_TYPE"] = "filesystem"
	Session(handler)
	handler.url_map.converters['regex']=RegularExpression
	CORS(handler)

	from connection import SocketConnection
	testplease=SocketConnection()
	
	@handler.route("/")
	def AB():
		indexresponse=make_response(render_template("/index.html"))
		return indexresponse
	@handler.route("/about")
	def CD():
		indexresponse=make_response(render_template("/index.html"))
		return indexresponse
	
	@handler.route("/register")
	def GH():
		indexresponse=make_response(render_template("/index.html"))
		return indexresponse

	@handler.route("/admin")
	def IJ():
		if 'secret_session' in session:
			indexresponse=make_response(render_template("/index.html"))
			return indexresponse
		else:
			return redirect(url_for('EF'))

	@handler.route("/login")
	def EF():
		if 'secret_session' in session:
			return redirect(url_for('IJ'))
		else:
			indexresponse=make_response(render_template("/index.html"))
			return indexresponse

	@handler.route("/feedback")
	def KL():
		if 'secret_session' in session:
			indexresponse=make_response(render_template("/index.html"))
			return indexresponse
		else:
			return redirect(url_for('EF'))

	@handler.route("/verify")
	def RR():
		if  'secret_session' in session:
			indexresponse=make_response(render_template("/index.html"))
			return indexresponse
		else:
			return redirect(url_for('EF'))

	@handler.route("/authorized")
	def OP():
		if 'secret_session' in session:
			indexresponse=make_response(render_template("/index.html"))
			return indexresponse
		else:
			return redirect(url_for('EF'))

	@handler.route("/admin/login")
	def QR():
		indexresponse=make_response(render_template("/index.html"))
		return indexresponse

	@handler.route("/Ambulance")
	def ST():
		if 'secret_session' in session:
			indexresponse=make_response(render_template("/index.html"))
			return indexresponse
		else:
			return redirect(url_for('EF'))

	@handler.route("/accounts")
	def UV():
		if 'secret_session' in session:
			indexresponse=make_response(render_template("/index.html"))
			return indexresponse
		else:
			return redirect(url_for('EF'))

	@handler.route("/user/api/login",methods=['POST','GET'])
	def Loginhandler():
		if request.method == "POST":
			userbody=request.get_json()
			username=userbody['username']
			password=userbody['password']
			return SqlApi().ApiAuthentication(user=username,passwd=password,method='login')
		
		error=make_response(json.dumps({'status':'Failed','message':'Method Not ALlowed'}),405)
		error.headers['Content-Type']="application/json"
		error.headers['Access-Control-Allow-Origin']="*"
		return error
	@handler.route("/user/api/new",methods=['POST'])
	def Registerhandler():
		if request.method == "POST":
				decoders=request.get_json()
				firstnames=decoders['Firstname']
				lastnames=decoders['Lastname']
				phones=decoders['Phone']
				address=decoders['Address']
				passwords=decoders['Password']
				usernames=decoders['Username']
				return SqlApi().ApiAuthentication(firstname=firstnames,lastname=lastnames,phone=phones,address=address,username=usernames,password=passwords,method="register")
		c=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
		c.headers['Content-Type']="application/json"
		return c

	@handler.route("/user/api/otp",methods=['POST'])
	def OTPSend():
		if request.method=="POST":
			userbody=request.get_json()
			token=userbody['authorization']
			email=userbody['email']
			return SqlApi().ApiAuthentication(authorization=token,emailuser=email,method='sendotp')
		b=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
		b.headers['Content-Type']='application/json'
		return b


	@handler.route("/user/api/verify",methods=['POST'])
	def VerifyUser():
		if request.method=="POST":				
			testbody=request.get_json()
			userotp=testbody['otp']
			userid=testbody['authorization']
			useremailid=testbody['emailid']
			return SqlApi().ApiAuthentication(UID=userid,checkemail=useremailid,otp=userotp,method='Verify')
		c=make_response(json.dumps({"status":"Failed","message":"Method Not ALlowed"}),405)
		c.headers['Content-Type']='application/json'
		return c

	@handler.route("/user/api/hospitals",methods=['PUT'])
	def Gethospitals():
		if 'secret_session' in session:
			if request.method == "PUT":
				user_body=request.get_json()
				token=user_body['authorization']
				email=user_body['email']
			else:
				c=make_response(json.dumps({"status":"Failed","message":"Method Not ALlowed"}),405)
				c.headers['Content-Type']='application/json'
				return c
			return SqlApi().ApiAuthentication(authorization=token,email=email,method='hospitalnames')
		else:
			return redirect(url_for('EF'))

	@handler.route("/user/api/apply",methods=['PUT'])
	def BookBedInHospital():
		if 'secret_session' in session:
			if request.method == "PUT":
				user_body=request.get_json()
				token=user_body['authorization']
				firstname=user_body['firstname']
				lastname=user_body['lastname']
				phone=user_body['phone']
				email=user_body['emailid']
			else:
				c=make_response(json.dumps({"status":"Failed","message":"Method Not Allowed"}),405)
				c.headers['Content-Type']='application/json'
				return c
			return SqlApi().ApiAuthentication(method="bookhospital",authorization=token,firstname=firstname,lastname=lastname,phone=phone,emailid=email)
		else:
			return redirect(url_for('EF'))

	@handler.route("/user/api/update",methods=['PUT'])
	def UpdateDetails():
		if 'secret_session' in session:
			if request.method == "PUT":
				try:
					updatebody=request.get_json()
					token=updatebody['authorization']
					emailid= updatebody['email']
					password= updatebody['password']
					firstname= updatebody['firstname']
					lastname= updatebody['lastname']
					phone= updatebody['phone']
				except:
					c=make_response(json.dumps({'status':'Failed','message':'Invalid Parameters'}),400)
					c.headers['Content-Type']="application/json"
					return c
				return SqlApi().ApiAuthentication(authorization=token,method="accountupdate",firstname=firstname,lastname=lastname,emailid=emailid,phone=phone,password=password)
			else:
				h=make_response(json.djmps({'status':'Failed','Message':'Method Not Allowed'}),405)
				h.headers['Content-Type']="application/json"
				return h
		else:
			return redirect(url_for('EF'))

	@handler.route("/user/account/details",methods=['GET'])
	def GetAccountDetail():
		if 'secret_session' in  session:
			if request.method == "GET":
				try:
					reqbody=request.headers['authorization']
				except:
					c=make_response(json.dumps({'status':'Failed','message':'Authorization Header Missing'}),400)
					c.headers['Content-Type']='application/json'
					return c
				return SqlApi().ApiAuthentication(authorization=reqbody,method='getdetail')
		else:
			return redirect(url_for('EF'))

	@handler.route("/user/api/delete",methods=['DELETE'])
	def DeleteAccount():
		if 'secret_session' in session:
			if request.method == 'DELETE':
				b=request.get_json()
				token=b['authorization']
				username=b['username']
				password=b['password']
			else:
				b=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
				b.headers['Content-Type']='application/json'
				return b
			return SqlApi().ApiAuthentication(authorization=token,username=username,password=password,method="deleteaccount")
		else:
			return redirect(url_for('EF'))

	@handler.route("/authadmin",methods=['POST','GET'])
	def AdminUser():
		if request.method == "POST":
			if request.remote_addr in ['192.168.56.101','192.168.56.1']:
				try:
					mybody=request.get_json()			
					username=mybody['username']
					password=mybody['password']
				except Exception as e:
					b=make_response(json.dumps({'status':'Failed','message':'Invalid Parameters'}),422)
					b.headers['Content-Type']=='application/json'
					return b
				return SqlApi().ApiAuthentication(method="adminlogin",username=username,password=password)
			else:
				b=make_response(json.dumps({'status':'Failed','message':'Only admins users are allowed'}))
				b.headers['Content-Type']='application/json'
				return b
		elif request.method == "GET":
			try:
				user_db=str(urllib.parse.unquote(request.url).split("=")[1].split("&")[0])
				authorization_header=request.headers['authorization']
			except Exception as e:
				print(e)
				c=make_response(json.dumps({'status':'Failed','message':'You are not authorized Person'}),401)
				c.headers['Content-Type']='application/json'
				return c
			return SqlApi().ApiAuthentication(method="getdatabase",authorization=authorization_header,email=user_db)
		else:
			pass
		c=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
		c.headers['Content-Type']='application/json'
		return c	

	@handler.route("/admin/login",methods=['GET'])
	def RedirectUser():
		if request.method== "GET":
			return redirect(url_for("AdminUser"))

	@handler.route("/details",methods=['GET'])
	def SendUserData():
		if request.method == 'GET':
			return SqlApi().ApiAuthentication(method="getcases")
		else:
			b=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
			b['Content-Type']='applicatino/json'
			return b


	@handler.route("/user/admin/account",methods=['POST'])
	def CheckDatabase():
		if 'secret_session' in session:
			if request.method == "POST":
				userbody=request.get_json()
				authorization_token=userbody['authorization']
				authorized_email=userbody['emailid']
			else:
				c=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
				c.headers['Content-Type']="application/json"
				return c
			return SqlApi().ApiAuthentication(method="getadminaccount",authorization=authorization_token,emailid=authorized_email)
		else:
			return redirect(url_for('EF'))

	@handler.route("/graph",methods=['GET'])
	def GetGraphData():
		if request.method == "GET":
			pass
		else:
			cs=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
			cs.headers['Content-Type']='application/json'
			return cs
		return SqlApi().ApiAuthentication(method="getgraph")

	@handler.route("/user/feedback",methods=['POST'])
	def GetFeedback():
		if 'secret_session' in session:
			if request.method == "POST":
				requestbody=request.get_json()
				token=requestbody['authorization']
				email=requestbody['Email']
				query=requestbody['query']
				return SqlApi().ApiAuthentication(method="feedback",authorization=token,emailid=email,address=query)

			cs=make_response(json.dumps({'status':'Failed','message':'Method Not Allowed'}),405)
			cs.headers['Content-Type']='application/json'
			return cs
		else:
			return redirect(url_for('EF'))

if __name__ == "__main__":
	MainServer.handler.run(host="0.0.0.0",port=8585,debug=True)