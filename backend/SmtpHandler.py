import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import  MIMEText
import time
from flask import make_response
import json

max_otp_valid_time=None

CONST_SUBJECT="Verify emailaddress"
class SMTPSender():
	
	def __init__(self,useremailid,otpsend):
		self.useremailid=useremailid
		self.otpsend=otpsend

	def Sender(self):
		try:
			message=MIMEMultipart()
			message['From']='---------------email---------'
			message['To']=self.useremailid
			message['Subject']=CONST_SUBJECT
			if type(self.otpsend) is int:
				message.attach(MIMEText('Verification code %s' % (int(self.otpsend)),'plain'))
			else:
				message.attach(MIMEText('Invitation link  %s' % (str(self.otpsend)),'plain'))
			mailhandler=smtplib.SMTP('smtp.gmail.com',587)
			mailhandler.starttls()
			mailhandler.login('---------------email---------','----password-----')
			finalmsg=message.as_string()
			mailhandler.sendmail('---------------email---------',self.useremailid,finalmsg)
		except Exception as e:
			c=make_response(json.dumps({'status':'Failed','message':'Verification code send failed please try again letter'}),400)
			c.headers['Content-Type']='application/json'
		d=make_response(json.dumps({'status':'OK','message':'success'}),200)
		d.headers['Content-Type']='application/json'
		return d
	

if __name__ == "__main__":
	pass