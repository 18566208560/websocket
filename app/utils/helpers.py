import os
import re
import time
import random
import socket
import string
import hashlib
import urllib3
import binascii
# import rsa
import requests
import ipaddress
import functools
import base64
from itsdangerous import TimedJSONWebSignatureSerializer as Its

def hash_password(password: str) -> str:
    """
    生成密码哈希
    :param password:
    :return:
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwd_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwd_hash = binascii.hexlify(pwd_hash)
    return (salt + pwd_hash).decode('ascii')


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    验证密码
    :param stored_password:
    :param provided_password:
    :return:
    """
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwd_hash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwd_hash = binascii.hexlify(pwd_hash).decode('ascii')
    return pwd_hash == stored_password


def page_to_offset(page: int, page_size: int) -> tuple:
    """
    根据页码信息生成query limit数据
    :param page:
    :param page_size:
    :return:
    """

    if page < 0:
        page = 1
    if page_size < 0:
        page_size = 10
    if page_size > 100:
        page_size = 100

    offset = (page - 1) * page_size

    return offset, page_size


def get_client_ip(request):
    """
    获取客户端 IP 地址
    :param request:
    :return:
    """

    proxy_ip = request.headers.get('X-Forwarded-For')
    if proxy_ip is not None:
        return proxy_ip.split(',')[0]
    else:
        return request.remote_addr


def to_integer(v, default=0):
    """
    转整形
    :param v:
    :param default:
    :return:
    """

    try:
        v = int(v)
        return v
    except:
        return default


def verify_ids(ids: str or list):
    """
    验证删除 url 后缀 eg: api/1,2,3
    不能为  0 空 重复
    """
    if not isinstance(ids, (str, list)):
        return False
    if isinstance(ids, str):
        ids = ids.split(',')

    ids_list = []
    for i in ids:
        i = to_integer(i)
        if i == 0:
            return False
        ids_list.append(i)

    if len(ids_list) == 0:
        return False
    if len(ids_list) != len(set(ids)):
        return False
    return ids_list


def not_empty_string(s):
    """
    检查字段是否为空
    :param s:
    :return:
    """

    if not isinstance(s, str):
        raise TypeError("Must be type 'str'")

    s = s.strip()
    if not s:
        raise ValueError("Must not be empty string")

    return s


def str_limit_1000(s):
    if not isinstance(s, str):
        raise TypeError("Must be type 'str'")

    s = s.strip()
    if len(s) > 1000:
        raise ValueError("String too long")

    return s


def str_limit_10000(s):
    if not isinstance(s, str):
        raise TypeError("Must be type 'str'")

    s = s.strip()
    if len(s) > 10000:
        raise ValueError("String too long")

    return s


def check_time_str_not_empty(s):
    """
    检查时间字符串是否为空
    :param s:
    :return:
    """

    if not isinstance(s, str):
        raise TypeError("Must be type 'str'")

    s = s.strip()
    try:
        time_arr = time.strptime(s, "%Y-%m-%d %H:%M:%S")
        time.mktime(time_arr)

        return s
    except:
        raise ValueError("Invalid time string '{}'".format(str(s)))


def check_time_str_to_int(s):
    """
    检查时间字符串并返回时间戳
    :param s:
    :return:
    """

    if s is None:
        return None

    if not isinstance(s, str):
        raise TypeError("Must be type 'str'")

    s = s.strip()

    if s == '':
        return None

    try:
        time_arr = time.strptime(s, "%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(time_arr)

        return timestamp
    except:
        raise ValueError("Invalid time string '{}'".format(str(s)))


def comma_to_tuple(s):
    """
    将以逗号分割的字符串转元组
    :param s:
    :return:
    """

    if s is None:
        return None

    if not isinstance(s, str):
        raise TypeError("Must be type 'str'")

    s = s.strip()
    if s == '':
        return tuple()
    else:
        return tuple(s.split(','))


def get_ip_segment(ip: str):
    """
    把 IP 段转换为无符号整数
    :param ip:
    :return:
    """

    if '/' in ip:
        _ip, mask_len = ip.split('/')
        _ip = int(ipaddress.IPv4Address(_ip))
        net_mask = 0xFFFFFFFF << (32 - to_integer(mask_len)) & 0xFFFFFFFF
        ip_start = _ip & net_mask
        ip_end = _ip | (~net_mask) & 0xFFFFFFFF
        ip_start = str(ipaddress.IPv4Address(ip_start))
        ip_end = str(ipaddress.IPv4Address(ip_end))
    elif '-' in ip:
        ip_start, ip_end = ip.split('-')
        if ip_end.isdigit():
            ip_end = '.'.join(ip_start.split('.')[:-1] + [ip_end])
    else:
        return int(ipaddress.IPv4Address(ip)), int(ipaddress.IPv4Address(ip))

    ip_start = int(ipaddress.IPv4Address(ip_start))
    ip_end = int(ipaddress.IPv4Address(ip_end))

    return ip_start, ip_end


def url_with_host(app, path: str, public=False) -> str:
    """
    根据 url 返回完整的地址
    避免 url_for 解析错误主机的问题
    :param app:
    :param path:
    :return:
    """

    path = path or ''

    if public:
        host_prefix = app.config.get('PUBLIC_HOST_PREFIX') or ''
    else:
        host_prefix = app.config.get('INNER_HOST_PREFIX') or ''

    if path.startswith('http') or path == '' or host_prefix == '':
        return path

    return '{}/{}'.format(host_prefix, path.lstrip('/'))


def check_input_str(s: str, min_len=None, max_len=None, chinese=False, letters=False, numbers=False, chars=None,
                    strict=False):
    """
    检查用户输入字符串
    :param s:
    :param min_len: 最小长度
    :param max_len: 最大长度
    :param chinese: 支持中文
    :param letters: 支持字母
    :param numbers: 支持数字
    :param chars: 支持自定义字符
    :param strict: 是否严格检查
    :return:
    """

    # 是否检查类型
    if not isinstance(s, str):
        return not strict

    s_len = len(s)
    if isinstance(min_len, int) and s_len < min_len:
        return False
    if isinstance(max_len, int) and s_len > max_len:
        return False

    allow_chars = ''
    if isinstance(chars, str):
        new_chars = ''
        for c in chars:
            if c == ' ':
                new_chars += '\\s'
            elif c == '\\':
                # 目前没有针对匹配'\'的字符, 直接跳过
                continue
            else:
                new_chars += '\\' + c
        allow_chars += new_chars
    if numbers:
        allow_chars += '0123456789'
    if letters:
        allow_chars += 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if chinese:
        allow_chars += '\\u4e00-\\u9fa5'

    if allow_chars == '':
        return True

    res = re.search('[^{}]'.format(allow_chars), s)
    if res is None:
        return True

    return False


def random_pass(length=8):
    a = string.ascii_letters + string.digits
    return "".join(random.sample(a, length))


def pagenate(data, current_page, per_page):
    x = (current_page - 1) * per_page
    y = current_page * per_page
    return data[x:y]


def check_port_is_open(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
        return True
    except socket.error as e:
        pass
    return False


def retry_if_false(count=1):
    def wrapper(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            for i in range(count):
                res = func(*args, **kwargs)
                if res:
                    return res
                time.sleep(0.5)
            return False

        return _wrapper

    return wrapper


@retry_if_false(count=3)
def send_training_status(url, data, train_id):
    """发送实训开始结束状态"""
    try:
        urllib3.disable_warnings()
        r = requests.post(url, json=data, timeout=2, verify=False)
        if r.status_code == requests.codes.ok:
            print("SEND_TRAIN_STATUS [%s] SUCCESS: %s" % (train_id, r.text))
            return True
        else:
            print("SEND_TRAIN_STATUS [%s] FAIL: %s" % (train_id, r.text))
            return False
    except Exception as e:
        print("SEND_TRAIN_STATUS [%s] ERROR: %s" % (train_id, e))
        return False


def get_ip_by_network(network, ips):
    """
    根据网络地址分配ip
    :param network: 网络地址
    :param ips: 去重ip列表
    :return: ip地址
    """
    i = 3
    new_ip = ""
    while True:
        if i > 254:
            break
        new_ip = re.sub(r"(\d*\.\d*\.\d*\.)(\d*)", r"\g<1>%s" % str(i), network)
        i += 1
        if new_ip not in ips:
            break

    return new_ip


class AttrDict(dict):
    '''
    字典转对象，适用于所有字典
    :returns: object
    :example:
        _dict = {'name':'test','age':10,'sex':'man'}
        human = AttrDict(_dict)
        print human.name
        print human.age
    '''

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def first(self, *names):
        for name in names:
            value = self.get(name)
            if value:
                return value


def genrate_user_token(data, secret_key, expires_in=60):
    """生成token"""
    its = Its(secret_key, expires_in)
    token = its.dumps(data)
    return token.decode()


def check_user_token(token, secret_key, expires_in=60):
    """校验token"""
    its = Its(secret_key, expires_in)
    try:
        data = its.loads(token)
    except:
        return None
    else:
        return data
#
# def rsa_encrypt(code, pubkey):
#     """
#     公钥加密码
#     :param code:
#     :param pubkey: 公钥
#     :return:
#     """
#     pubkey = rsa.PublicKey.load_pkcs1(pubkey)
#     # 明文编码格式
#     content = code.encode("utf-8")
#     # 公钥加密
#     crypto = rsa.encrypt(content, pubkey)
#     crypto = binascii.hexlify(crypto)
#     return crypto.decode("utf-8")
#
#
# # rsa解密
# def rsa_decrypt(code, privkey):
#     """
#     私钥解密
#     :param code:
#     :param privkey: 私钥
#     :return:
#     """
#     try:
#         privkey = rsa.PrivateKey.load_pkcs1(privkey)
#         code = code.encode("utf-8")
#         code = binascii.unhexlify(code)
#         content = rsa.decrypt(code, privkey)
#     except Exception as e:
#         return None
#     return content.decode("utf-8")


def gen_uuid(code, secret_key):
    """
    生成uuid
    :param code:
    :param secret_key:
    :param pubkey:
    :return:
    """
    code = code.lower()
    code = hash_password(code)
    uuid = genrate_user_token(code, secret_key)
    return uuid


def verify_uuid(uuid, secret_key, contnet):
    """
    验证uuid
    :param uuid:
    :param secret_key:
    :param privkey:
    :return:
    """
    contnet = contnet.lower()
    code = check_user_token(uuid, secret_key)
    if not code:
        return None
    return verify_password(code, contnet)
