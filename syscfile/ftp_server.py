from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

class MyEventHandler(FTPHandler):
	
	def on_connect(self):
		''' When client connected..'''
		print "%s:%s connected"%(self.remote_ip, self.remote_port)

	def on_login(self, username):
		''' When user login'''



def main():
	authorizer = DummyAuthorizer()
	authorizer.add_user("user","123654",homedir = ".", perm="elradfmw")
	authorizer.add_anonymous(homedir=".")

	server_handler = MyEventHandler
	server_handler.authorizer = authorizer
	server = FTPServer({"", 2121}, server_handler)
	server.serve_forever()




if __name__ == "__main__":
	main()
