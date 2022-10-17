from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import requests
import frida
import sys, getopt
ECHO_PORT = 28080
BURP_PORT = 8080
script=None

class global_script():
    script=None
    @staticmethod
    def init_script(self,con):
        print(type(con))
        self.script=con()

class RequestHandler(BaseHTTPRequestHandler):
    def do_REQUEST(self):
        content_length = int(self.headers.get('content-length', 0))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.rfile.read(content_length))
    do_RESPONSE = do_REQUEST


def echo_server_thread():
    print('start echo server at port {}'.format(ECHO_PORT))
    server = HTTPServer(('', ECHO_PORT), RequestHandler)
    server.serve_forever()

def on_message(message, data):
    if message['type'] == 'send':
        payload = message['payload']
        _type, data = payload['type'], payload['data']
        if _type == 'REQ':
            data = str(data)
            r = requests.request('REQUEST', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                 proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                 data=data.encode('utf-8'))
            script.post({'type': 'NEW_REQ', 'payload': r.text})
        elif _type == 'RESP':
            r = requests.request('RESPONSE', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                 proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                 data=data.encode('utf-8'))
            script.post({'type': 'NEW_RESP', 'payload': r.text})
def start(argv):
    global script
    t = Thread(target=echo_server_thread)
    t.daemon = True
    t.start()
    hook_type=""
    mini_pid=""
    
    try:
      opts, args = getopt.getopt(argv,"ht:p:",["type=","pid="])
    except getopt.GetoptError:
        print("python miniprogram_cloudfunctions_request.py -t mac -p 11539")
        print("python miniprogram_cloudfunctions_request.py -t ios ")
        sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print("python miniprogram_cloudfunctions_request.py -t mac -p 11539")
         print("python miniprogram_cloudfunctions_request.py -t ios ")
         sys.exit()
      elif opt in ("-t", "--type"):
         hook_type = arg
      elif opt in ("-p", "--pid"):
         mini_pid = arg
    if(hook_type=="ios"):
        session = frida.get_usb_device().attach('微信') # IOS 移动端
        with open("ios.js") as f:
            script=session.create_script(f.read())
        script.on('message', on_message)
        script.load()
        sys.stdin.read()
    elif(hook_type=="mac"):
        session = frida.attach(int(mini_pid)) # macos电脑端 ps -ef |grep Mini
        #session = frida.attach(21831) # macos电脑端 ps -ef |grep Mini
        with open("macos.js") as f:
             script=session.create_script(f.read())
        script.on('message', on_message)
        script.load()
        sys.stdin.read()
        
    else:
        print("python miniprogram_cloudfunctions_request.py -t mac -p 11539")
        print("python miniprogram_cloudfunctions_request.py -t ios ")
        print("安卓、windows 微信小程序暂未支持")
        sys.exit()
    
if __name__=="__main__":
    start(sys.argv[1:])