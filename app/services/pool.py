# -*- coding: utf-8 -*-
"""
FileName: clickhouse_manager.py
Desc    : clickhouse 数据库连接管理对象
Author  : lwm
Date    : 20/10/20
"""
import redis
import logging
from dbutils.persistent_db import PersistentDB
from clickhouse_driver import dbapi
from app.utils.singleton import Singleton

log = logging.getLogger("task")


class ClickHouseManager(metaclass=Singleton):

    def __init__(self, host, port, user, password, database):
        if not hasattr(self, "__pool"):
            ch_cfg = dict(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            self.__pool = PersistentDB(creator=dbapi, **ch_cfg)

    @property
    def pool(self):
        return self.__pool


class BaseModel(object):
    def __init__(self, app):
        self.ch_client = ClickHouseManager(**app.config.get('CK_URI')).pool

    def execute(self, sql):
        """执行sql语句"""
        try:
            conn = self.ch_client.connection()
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
        except Exception as e:
            log.error(e)
            raise e
        else:
            return result
        finally:
            if "cur" in locals():
                cur.close()
            if "conn" in locals():
                conn.close()

    def to_dict(self, field, result):
        """把元组结果转化为字典值"""
        return dict(zip(field, result))


def ch_pool_init(app):
    app.ck = BaseModel(app)


def redis_pool_init(app):
    app.cli = redis.Redis.from_url(app.config.get('REDIS_URI'))
