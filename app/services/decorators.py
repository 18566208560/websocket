from functools import wraps
from flask import g, request, current_app
from app.services.response import res_json
from app.repositories.tq30.user import UserRepository
from app.utils.config import get_option
from app.utils.helpers import check_user_token


def api_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Api-Token') or request.args.get('token')
        if token is None or token.strip() == '':
            return res_json(code='token_missing')

        # 校验token
        login_expires = int(get_option(option="login_expires"))
        data = check_user_token(token, current_app.config.get("SECRET_KEY"), expires_in=login_expires)
        if not data:
            return res_json(code="invalid_token")

        token = data.get("uuid")

        user = UserRepository.get_user_by_token(token)
        if user is None:
            return res_json(code='invalid_token')

        # 设置user
        g.user = user

        return func(*args, **kwargs)

    return wrapper


def allow_roles(roles: tuple):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查是否已经登录
            # 避免装饰器使用顺序问题导致未登录
            # 该装饰器应在 auth 前面
            if g.user is None:
                return func(*args, **kwargs)

            # 检查权限
            if g.user.role not in roles:
                return res_json(code='permission_denied')

            return func(*args, **kwargs)

        return wrapper

    return actual_decorator


def process_error(func):
    """处理接口异常"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            code = "system_error"

            # 参数错误此处不处理
            if hasattr(e, "code"):
                if e.code == 400:
                    raise e

            # 主动触发异常捕获
            if hasattr(e, "args"):
                code = e.args[0] if e.args else code

            # 其它未知异常捕获
            e.data = res_json(code=code, ret_json=True)
            raise e

    return wrapper



def hash_cache(redis_cli, key):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal redis_cli
            nonlocal key
            cache_map = redis_cli.hgetall(key)
            if cache_map:
                return cache_map
            else:
                cache_map = func(*args, **kwargs)
                redis_cli.hset(key, mapping=cache_map)
            return cache_map
        return wrapper
    return decorator