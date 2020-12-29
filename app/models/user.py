from sqlalchemy.dialects.mysql import INTEGER
from app.models import db, BaseModel


class UserModel(db.Model, BaseModel):
    """
    用户
    """
    __bind_key__ = "tq30"
    __tablename__ = 'user'
    __table_args__ = {
        'comment': '用户表'
    }

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    username = db.Column(db.String(55), nullable=False, comment='用户名')
    password = db.Column(db.String(255), nullable=False, comment='密码')
    display_name = db.Column(db.String(55), nullable=False, comment='显示名称')
    gender = db.Column(INTEGER(unsigned=True), default=0, nullable=False, comment='姓别(0未知 1女 2男)')
    company = db.Column(db.String(60), default='', nullable=False, comment='公司/组织')
    image = db.Column(db.String(1024), default='', nullable=False, comment='图片说明、头像')
    role = db.Column(INTEGER(unsigned=True), default=3, nullable=False,
                     comment='角色 1 admin, 2 teacher, 3 student, 4 observer')
    api_token = db.Column(db.String(32), default='', nullable=False, comment='Api_Token')
    token_expires = db.Column(INTEGER(unsigned=True), default=0, nullable=False, comment='Token过期时间')
    login_ip = db.Column(db.String(255), default='', nullable=False, comment='登录IP')
    signature = db.Column(db.String(1024), default='', nullable=False, comment='个性签名')
    created_at = db.Column(INTEGER(unsigned=True), default=0, nullable=False, comment='创建时间')
    updated_at = db.Column(INTEGER(unsigned=True), default=0, nullable=False, comment='更新时间')
    deleted_at = db.Column(INTEGER(unsigned=True), default=0, nullable=False, comment='删除时间')

    ROLE_ADMIN = 1
    ROLE_TEACHER = 2
    ROLE_STUDENT = 3
    ROLE_OBSERVER = 4

    def __repr__(self):
        return '<User {}>'.format(self.username)
