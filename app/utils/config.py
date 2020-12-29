import configparser
import os
from app.settings import DefaultConfig

conf_file = DefaultConfig.CONF_FILE


def get_config_handler(path):
    """
    返回配置文件操作句柄
    :param path: 文件路径
    :return config: 配置文件操作句柄
    """
    config = configparser.RawConfigParser()
    config.read(path, encoding="utf-8")
    return config


def get_option(path=conf_file, section="common", option=None, default=None):
    """
    获取配置
    :param path: 配置文件路径
    :param section: 节点
    :param option: 节点中的项
    :param default: 默认数据
    :return value: 获取到的数据
    """
    config = get_config_handler(path)
    try:
        value = config.get(section, option)
        if value is None:
            return default
        else:
            return value
    except Exception as e:
        return default


def set_option(path=conf_file, section=conf_file, option="common", value=None):
    """
    配置配置文件
    :param path: 配置文件路径
    :param section: 节点
    :param option: 节点中的项
    :param value: 写入项中的数据
    """
    config = get_config_handler(path)
    config.set(section, option, value)
    config.write(open(path, 'r+'))
