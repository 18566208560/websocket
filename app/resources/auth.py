import time
from flask import g, request, current_app, make_response

from app.repositories.scheduler import SchedulerRepository
from app.resources.base import BaseResource, ApiResource
from app.services.response import res_json
from app.utils.captcha.captcha import captcha
from app.utils.helpers import gen_uuid, verify_uuid


class AuthLoginResource(BaseResource):
    """
    用户登录
    """

    def post(self):
        self.parser.add_argument('username', type=not_empty_string, location="json", required=True)
        self.parser.add_argument('password', type=not_empty_string, location="json", required=True)
        self.parser.add_argument('uuid', type=str, location='json', required=True)
        self.parser.add_argument('content', type=str, location='json', required=True)
        args = self.parse_args()

        if not verify_uuid(args.get("uuid"), current_app.config.get("CAPTCHA_SECRET_KEY"), args.get("content")):
            return res_json(code="captcha_error")

        user = UserRepository.get_user_by_username_and_password(args.get('username'), gen_md5(args.get('password')))
        if user is None:
            return res_json(code='invalid_auth_params')

        if user.role == 3:
            contest = ContestModel.get_model_by_fields(deleted_at=0, active=1)
            if not contest or contest.status == 0:
                return res_json(code="contest_not_start")

        try:
            # 填写当前登录信息
            user.login_ip = get_client_ip(request)
            user.login_time = int(time.time())

            user_data = user.res_format(password=False, api_token=False, token_expires=False, deleted_at=False)
            login_expires = int(get_option(option="login_expires"))

            # 更新 Api token
            new_uuid = gen_md5(str(uuid.uuid4()))
            new_token = genrate_user_token({"uuid": new_uuid}, current_app.config.get("SECRET_KEY"),
                                           expires_in=login_expires)
            UserRepository.update_user_token_by_model(user, new_uuid)

            user_data['api_token'] = new_token

            # 添加用户所在团队信息
            if user.role == 3:
                train = get_train_id()
                if isinstance(train, str):
                    return res_json(code=train)
                team = FlagRepository.get_team_train_user(train, user)
                if not team:
                    return res_json(code="invalid_user")
                user_data['team'] = team.res_format_only(id=True, team_name=True, team_image=True)

        except Exception as e:
            current_app.logger.exception(e)
            return res_json(code='user_login_fail')

        return res_json(data=user_data)


class AuthLogoutResource(ApiResource):
    """
    用户登出
    """

    def post(self):
        try:
            UserRepository.update_user_token_by_model(g.user, '')
        except Exception as e:
            current_app.logger.exception(e)
            return res_json(code='user_logout_fail')

        return res_json()


class AuthProfileResource(ApiResource):
    """
    认证用户信息
    """

    def get(self):
        """获取认证用户信息"""
        data = UserRepository.gen_profile_user_data(g.user)
        return res_json(data=data)

    def patch(self):
        """更新认证用户信息"""
        self.parser.add_argument('display_name', type=str, location='form', default=None)
        self.parser.add_argument('old_password', type=str, location='form', trim=True, default='')
        self.parser.add_argument('new_password', type=str, location='form', trim=True, default='')
        self.parser.add_argument('new_password2', type=str, location='form', trim=True, default='')
        self.parser.add_argument('image', type=FileStorage, location='files')

        args = self.parse_args()

        if args.get("display_name") is not None:
            # 检查姓名格式
            if not UserRepository.check_display_name(args.get('display_name')):
                return res_json(code='invalid_display_name')

            # 检查名称重复
            if UserRepository.verify_login_name(args.get("display_name"), g.user.id):
                return res_json(code="duplicate_display_name")

        # 密码三个参数必须同时不为空
        if args.get("new_password") or args.get("new_password2"):
            if not args.get("new_password") and args.get("new_password2"):
                return res_json(code="invalid_new_password")
            if not args.get("old_password"):
                return res_json(code='invalid_old_password')

        # 检查是否修改密码
        if args.get('old_password') != '':
            if gen_md5(args.get('old_password')) != g.user.password:
                return res_json(code='invalid_old_password')
            if args.get('new_password') == '' or args.get('new_password2') == '' or args.get(
                    'new_password') != args.get('new_password2'):
                return res_json(code='invalid_new_password')

            # 检查密码格式
            if args.get('new_password') == g.user.username:
                return res_json(code='same_username_password')
            if not UserRepository.check_password(args.get('new_password')):
                return res_json(code='invalid_password')

            args['api_token'] = ''  # 已经修改了密码, 需要重新登录
            args['new_password'] = gen_md5(args.get('new_password'))
        else:
            args['api_token'] = g.user.api_token
            args['new_password'] = g.user.password

        # 检查头像后缀
        if args.get('image') is not None:
            if not check_file_extension(args.get('image')):
                return res_json(code='invalid_image_extension')

        old_image = g.user.image

        try:
            # 头像
            args['image'] = save_uploaded_image(current_app, args.get('image'), 'profile_')

            UserRepository.update_user_profile_by_model(g.user, args.get('display_name'), args.get('new_password'),
                                                        args.get('api_token'), image=args.get('image'))
        except Exception as e:
            current_app.logger.exception(e)
            args.get("image") and remove_file_by_link(current_app, args['image'])
            return res_json(code='update_profile_fail')

        # 清除旧头像文件
        if args.get('image') is not None:
            remove_file_by_link(current_app, old_image)

        # 返回更新后的用户信息
        user = UserRepository.get_user_by_id(g.user.id)
        data = UserRepository.gen_profile_user_data(user)
        return res_json(data=data)


class CaptchaResource(BaseResource):
    """
    验证码
    """

    def get(self):
        try:
            text, image = captcha.generate_captcha()

        except Exception as e:
            current_app.logger.exception("验证码生成错误")
        else:
            uuid = gen_uuid(text, current_app.config.get("CAPTCHA_SECRET_KEY"))
            response = make_response(image)
            response.headers["uuid"] = uuid
            response.headers['Content-Type'] = 'image/gif'
            return response


class TaskResource(ApiResource):

    def post(self):
        try:
            SchedulerRepository.create_scheduler("recovery_snapshot", "recovery_snapshot", params={}, trigger="date",
                                                 start_time=int(time.time()))
        except Exception as e:
            current_app.exception(e)
            return res_json(code="")
        return res_json()
