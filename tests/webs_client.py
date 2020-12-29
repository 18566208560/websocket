
import websocket
import time
import threading
import ssl

def webs():
    #s = websocket.create_connection("wss://127.0.0.1:10443/api/ws", sslopt={"cert_reqs": ssl.CERT_NONE})
    #s = websocket.create_connection("wss://127.0.0.1:10443/api/ws", ssl=ssl.SSLContext(protocol=ssl.PROTOCOL_TLS))
    s = websocket.create_connection("ws://172.33.0.9:5000/api/ws")
    print("Sending Hello, World...")

    s.send("Hello, World")
    print("sent")
    print("Receiving")
    s.send("Hello, World{:0>9d}".format(1))
    a = 1
    while 1:
        
        result = s.recv()
        print("Received '%s'" % result)

        a += 1
    s.close()
    
   

for i in range(1):
    t = threading.Thread(target=webs)
    t.start()
    
