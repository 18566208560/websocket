import uwsgi 
import time
import gevent
def func(environ, start_response):
    for key,val in environ.items():
        if key == "HTTP_SEC_WEBSOCKET_KEY":
            print(key,"== ",val)


    uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
    print("websockets...")

    websocket_fd = uwsgi.connection_fd()
    core_id = environ['HTTP_SEC_WEBSOCKET_KEY']
    print(websocket_fd, core_id)

    while True:
        ready = gevent.select.select([websocket_fd], [], [], 4.0)
        if ready[0]:
            print(ready)

            msg = uwsgi.websocket_recv_nb()
            print("msg ",msg)
            uwsgi.websocket_send("xxxooo")
            gevent.sleep(1)



application = func

class WServer():

    def init(self, rhost, rport, rdb=0):
        uwsgi.websocket_handshake()
        self.r = redis.StrictRedis(host=rhost, port=srport, db=rdb)

        channel = self.r.pubsub()
        channel.subscribe(self.room)

        websocket_fd = uwsgi.connection_fd()
        redis_fd = channel.connection._sock.fileno()


        while True:
            ready = gevent.select.select([websocket_fd, redis_fd], [], [], 4.0)
            if not ready[0]:
                uwsgi.websocket_recv_nb()
            for fd in ready[0]:
                if fd == websocket_fd:
                    try:
                        msg = uwsgi.websocket_recv_nb()
                    except IOError:
                        self.end(core_id)
                        return ""
                    if msg:
                        self.websocket(core_id, msg)
                elif fd == redis_fd:
                    msg = channel.parse_response()
                    if msg[0] == 'message':
                        uwsgi.websocket_send(msg[2])

                        修复bug代码同步，研究比赛数据websocket传输