# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import random
import re
import time

from app.utils.logger_helper import get_logger
from app.settings import base_path

__all__ = ['add_rules']

HOSTS_PATH = os.path.join(base_path, 'config', 'hosts')

g_logger = get_logger('iptables_dnat')


class InvalidParam(Exception):
    """无效的参数"""
    pass


class AnsibleExecuteError(Exception):
    """调用Ansible执行ssh命令时发生错误"""
    pass


def run_shell_result(cmd):
    """执行cmd并返回输出"""
    g_logger.debug('run cmd: %s' % cmd)
    return os.popen(cmd).read()


def clear_rules():
    """清空PREROUTING链中的所有规则"""
    result = run_shell_result(
        'ansible -i %s all -a "iptables -t nat -F PREROUTING"' % HOSTS_PATH
    )
    if result.find('| FAILED |') != -1:
        raise AnsibleExecuteError(result)

    return True


def save_iptables():
    """规则持久化"""
    result = run_shell_result(
        'ansible -i %s all -a "service iptables save"' % HOSTS_PATH
    )
    if result.find('| FAILED |') != -1:
        raise AnsibleExecuteError(result)

    return True


def _format_iptables_cmd(rule):
    """格式化iptables规则"""
    comment = '%s_%s -> %s_%s (DNAT use %s)' % (
        rule['destination'],
        rule.get('destination_port'),
        rule['to_destination'],
        rule.get('to_port'),
        rule.get('protocol', 'all')
    )

    destination = '%s' % rule['destination']
    if rule.get('destination_port'):
        destination = '%s --dport %s' % (destination, rule['destination_port'])

    to_destination = '%s' % rule['to_destination']
    if rule.get('to_port'):
        to_destination = '%s:%s' % (to_destination, rule['to_port'])

    iptables_cmd = 'iptables -t nat -I PREROUTING -p %s -d %s -m comment --comment \'%s\' -j DNAT --to-destination %s' % (
        rule.get('protocol', 'all'),
        destination,
        comment,
        to_destination
    )

    return iptables_cmd


def _add_rule(iptables_cmd):
    """添加DNAT规则"""
    result = run_shell_result(
        'ansible -i %s all -a "%s"' % (HOSTS_PATH, iptables_cmd)
    )

    if result.find('| FAILED |') != -1:
        raise AnsibleExecuteError(result)


def add_rules(rules):
    """
    添加DNAT规则

    Args:
        rules (list): DNAT规则列表, 每一项为一个dict, dict包含如下字段
            destination (str): 目的IP, iptables DNAT宿主机IP
            destination_port (int): 目的端口, 默认: ``None``
            to_destination (str): DNAT到的IP
            to_port (int): DNAT到的端口, 默认: ``None``
            protocol (str): 协议 (tcp/udp/all), 默认: ``all``

    Returns:
        bool: 添加成功返回True, 否则将抛出异常

    Raises:
        InvalidParam: 无效的参数
        AnsibleExecuteError: 调用Ansible执行ssh命令时发生错误

    Note:
        由于添加规则前会先清除所有已存在的DNAT规则, 所以需要一次性将所有的rules传递进来, 不能分多次添加
    """
    if not rules:
        raise InvalidParam('rules is None')

    if not isinstance(rules, list):
        raise InvalidParam('rules type: %s is not list' % type(rules))

    clear_rules()

    for rule in rules:
        iptables_cmd = _format_iptables_cmd(rule)
        _add_rule(iptables_cmd)

    save_iptables()

    return True


def test_add_rules_error():
    rules = [
        {
            'destination': '192.168.166.177',
            'to_destination': '10.10.10.10000000',
            'protocol': 'all'
        },
    ]

    try:
        add_rules(rules)
    except AnsibleExecuteError as e:
        print(e.message)


def _print_rules():
    """输出已存在的规则方便测试"""
    result = run_shell_result(
        'ansible -i %s all -a "iptables -nL -t nat"' % HOSTS_PATH
    )
    pattern = re.compile('.*?/\* (.*?)\*/', re.S)
    items = re.findall(pattern, result)

    if items:
        for item in items:
            print(item)
    else:
        print('no rules')

    return items


if __name__ == '__main__':
    rules = [
        {
            'destination': '192.168.166.168',
            'to_destination': '10.10.10.10',
            'protocol': 'all'
        },
        {
            'destination': '192.168.166.177',
            'to_destination': '10.10.10.11',
        }
    ]

    while 1:
        print('start add rules...')

        add_rules(rules)
        # test_add_rules_error()

        print('start verification add rules...')

        if not _print_rules():
            raise ValueError('not found rules after add rules...')

        time.sleep(random.randint(1, 10))

        print('start clear rules...')

        clear_rules()
        save_iptables()

        print('start verification clear rules...')

        if _print_rules():
            raise ValueError('found rules after clear rules...')

        time.sleep(random.randint(5, 15))
