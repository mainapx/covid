from socketio import Server;import eventlet
import socketio

def background(serverevent,mysid):
	exec(str(serverevent))

class SocketConnection:
	def __init__(self):
		try:
			socketconnection=socketio.Server(async_mode="threading",cors_allowed_origins="*")
			socketconnection.wsgi_app=socketio.WSGIApp(socketconnection,handler.wsgi_app)


			@socketconnection.event(namespace="/token")
			def connect(sid, environ):
				socketconnection.start_background_task(self.background_thread,"socketconnection.emit('ReceviedConnect',{'data':'OK Connected'},namespace='/token',room=mysid)",sid)

			@socketconnection.event(namespace="/token")
			def SendToken(sid,message):
				socketconnection.start_background_task(self.background_thread,"socketconnection.emit('ReceiveToken',{'data':authorized_token},namespace='/token',room=mysid",sid)

			@socketconnection.event(namespace="/token")
			def disconnect(sid):
				socketconnection.start_background_task(self.background_thread,"socketconnection.emit('Disconnected_Request',{'data':'Disonnected From Server By...'},namespace='/token',room=mysid)",sid)
		except:
			pass