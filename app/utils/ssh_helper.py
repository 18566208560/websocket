
import os
import sys
import socket
import random
import string
import re
from warnings import catch_warnings, simplefilter
from invoke import pty_size
from invoke.runners import Runner
from fabric.runners import Remote
from invoke.exceptions import CommandTimedOut

from app.utils.logger_helper import get_logger

with catch_warnings(record=True):
    simplefilter('ignore')
    from fabric import Connection

LOG = get_logger("ssh")

class LoggerStream(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    新建一个有write和flush的类，主要用于fabric stdout/stderr重定向输出日志文件。
    """

    def __init__(self, logger, log_level=None):
        self.logger = logger
        if log_level is None:
            self.log_level = logger.getEffectiveLevel()
        else:
            self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self, *args, **kwargs):
        pass

STREAM = LoggerStream(LOG)

class Error(Exception):
    def __init__(self, message):
        self.message = message
        super(Error, self).__init__(message)

    def __str__(self):
        return repr(self.message)


def _filter_except(exc):
    '''
    过滤exception的消息
    '''
    if hasattr(exc, 'message'):
        return exc.message
    else:
        return str(exc)


def _filter_message(res):
    '''过滤fabric结果'''
    result = res.stdout
    stderr = res.stderr
    if result.startswith('bash') or result.startswith('ksh'):
        result = result[result.index(':') + 1:].lstrip()
    if len(stderr.strip()) == 0 or len(result.strip()) == 0:
        LOG.warning(str(res))
        result = 'Unknown internal error.'
    if len(stderr.strip()):
        result = stderr
    return result


class CmdClient(object):
    """
    ssh客户端
    """

    def __init__(self, ip=None, port=22, user=None, password=None,
            shell=None, use_shell=False, pty=False, sh_env=None):
        """
        初始化
        :param ip: ip地址
        :param port: 端口
        :param user: 用户
        :param password: 密码
        :param shell: 远程命令执行的shell命令,如：sh -c "ls" sh就是这个shell
        :param use_shell: 是否使用shell命令
        :param pty: 是否打开pty
        :param sh_env: 执行命令的环境变量
        """
        self.user = user
        self.password = password
        self.port = port
        self.ip = ip
        self.shell = shell
        self.use_shell = use_shell
        self.pty = pty
        self.sh_env = sh_env

        self.connection_str = ('%s@%s:%s' % (self.user, self.ip, self.port))

        self.con = Connection(user=user, host="%s:%s"%(self.ip, self.port),
                connect_kwargs={"password": self.password}, inline_ssh_env=True)
        self.set_con_env()

        #scp上传文件
        self.put = self.con.put
        #scp下载文件
        self.get = self.con.get

    def _set_env(self, env_dict):
        """
        配置环境
        """
        env = self.con.config.run.get("env", {})
        for k, v in env_dict.items():
            env[k] = v
        self.con.config.run['env'] = env
        self.con.config.inline_ssh_env = True

    def set_con_env(self):
        """
        配置环境信息
        """
        if self.sh_env and type(self.sh_env) == dict:
            self._set_env(self.sh_env)

        self.con.config.run['use_shell'] = False
        if self.pty:
            self.con.config.run['pty'] = True
        if self.use_shell:
            self.con.config.run['use_shell'] = True
            self.con.config.run['shell'] = self.shell

    def run(self, cmd, ignore=False, pty=False, timeout=None, sh_env=None,
            shell=None, use_shell=False, encounted_raise=None, sudo=False):
        """
        运行命令
        :param cmd: 命令
        :param ignore: 是否忽略错误
        :param pty: 是否打开pty
        :param timeout: 命令超时间
        :param sh_env: 执行命令的环境变量
        :param shell: 远程命令执行的shell命令,如：sh -c "ls" sh就是这个shell
        :param use_shell: 是否使用shell命令
        :param encounted_raise: 遇到错误抛出指定的错误
        :param sudo: 使用使用sudo权限运行命令
        """
        try:
            LOG.debug('[%s] run: %s' % (self.connection_str, cmd))
            if type(sh_env) == dict:
                self._set_env(sh_env)

            if pty:
                self.con.config.run['pty'] = True
            self.con.config.run['use_shell'] = use_shell
            self.con.config.run['shell'] = shell
            if sudo:
                result = self.con.sudo(cmd, timeout=timeout, warn=True, out_stream=STREAM,
                        err_stream=STREAM, in_stream=False)
            else:
                result = self.con.run(cmd, timeout=timeout, warn=True, out_stream=STREAM,
                    err_stream=STREAM, in_stream=False)

            if result.return_code != 0 and not ignore:
                error = _filter_message(result)
                LOG.error('Command: \'%s\'.' % cmd)
                LOG.error('Error: %s.' % error)
                raise Error('Error: %s.' % error)
            elif result.return_code != 0 and encounted_raise:
                if encounted_raise in result.stdout:
                    error = _filter_message(result)
                    LOG.error('Command: \'%s\'.' % cmd)
                    LOG.error('Error: %s.' % error)
                    raise Error('Error: %s.' % error)
            return result

        except (socket.timeout, socket.error) as toerr:
            LOG.exception(_filter_except(toerr))
            raise Error(_filter_except(toerr))
        except Error as ex:
            err = _filter_except(ex)
            LOG.info(err)
            if 'password' in str(err):
                error_msg = SUDO_PASSWD % self.connection_str
                raise Error(error_msg)
            else:
                raise Error(err)
        finally:
            self.set_con_env()

    def close(self):
        """
        关闭连接
        """
        self.con.close()
