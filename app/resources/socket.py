# -*- coding: utf-8 -*-
# @Time        : 2020/12/17 10:35
# @Author      : lijian
# @Description :
import json
import time

import uwsgi
import gevent
from flask import current_app, request
from app.resources.base import ApiResource


class SocketResource(ApiResource):

    def get(self):
        """
        websocket接口
        """
        # 校验
        if 1 > 2:
            return "not_found", 400

        # 标识请求唯一ID
        ws_key = request.headers.get('Sec-Websocket-Key')
        origin = request.headers.get('Origin')

        uwsgi.websocket_handshake(ws_key, origin)

        # 发送初始数据
        self.init_msg()

        # 订阅消息
        channel = current_app.cli.pubsub()
        channel.subscribe(f"team_1")
        channel.subscribe("contest")

        websocket_fd = uwsgi.connection_fd()
        redis_fd = channel.connection._sock.fileno()

        while True:
            ready = gevent.select.select([websocket_fd, redis_fd], [], [], 3)
            if not ready[0]:
                # 调用uwsgi的websocket_recv_nb激活ping/pong，避免断开连接
                uwsgi.websocket_recv_nb()

            for fd in ready[0]:
                if fd == websocket_fd:
                    # 异步接收消息
                    try:
                        msg = uwsgi.websocket_recv_nb()
                    except Exception as e:
                        current_app.logger.error(e)
                        return
                    if msg:
                        self.process_msg(ws_key, msg)
                elif fd == redis_fd:
                    # 接收订阅消息并发送 msg 格式  [b'message', b'big_screen', b'6EHF']
                    msg = channel.parse_response()
                    if msg[0] == b'message':
                        uwsgi.websocket_send(msg[2])

    def process_msg(self, ws_key, msg):
        """处理消息"""
        pass

    def send(self, msg):
        """发送消息"""
        uwsgi.websocket_send(msg)

    def init_msg(self):
        """初始化消息"""
        self.send("init")
