# -*- coding: utf-8 -*-#
"""
# FileName: singleton
# Desc    : 单列
# Author  : luweimin
# Date    : 2020/6/16
"""
import threading
from functools import wraps


class Singleton(type):
    """
    通过元类来实现单列
    父类实现了单例,子类也是单例
    """
    _instance_lock = threading.Lock()

    # 元类的__init__方法负责在类创建后初始化类属性
    def __init__(cls, *args, **kwargs):
        # 虽然子类SubClass创建时继承了基类MyClass的类属性_instance，但是会在此处被重置为None，从而SubClass也是单例模式
        cls._instance = None
        super(Singleton, cls).__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            with Singleton._instance_lock:
                if cls._instance is None:
                    # 通过super函数调用父元类type的__call__方法完成实例化
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


def singleton(fun):
    """
    通过装饰器实现的单例
    没有实现线程安全
    :param fun:
    :return:
    """
    _instance = {}

    @wraps(fun)
    def _singleton(*args, **kargs):
        if fun not in _instance:
            _instance[fun] = fun(*args, **kargs)
        return _instance[fun]

    return _singleton
