from sqlalchemy.dialects.mysql import TINYINT, INTEGER
from app.models import db, BaseModel


class SchedulerModel(db.Model, BaseModel):
    """
    任务调度表
    """

    __tablename__ = "schedule"
    __table_args__ = {
        "comment": "任务调度表"
    }

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, comment='任务名称')
    status = db.Column(INTEGER(unsigned=True), nullable=False, default=0,
                       comment="任务状态, 0:未开始, 1:进行中, 2:已结束")
    params = db.Column(db.Text, nullable=True, comment="任务参数,json格式存放")
    create_time = db.Column(INTEGER(unsigned=True), nullable=False, comment="创建时间")
    trigger = db.Column(db.String(255), nullable=True,
                        comment='触发器 date:指定时间运行 interval:周期性运行,指定间隔时间')
    minutes = db.Column(INTEGER(unsigned=True), nullable=False, default=0, comment="间隔分钟数")
    start_time = db.Column(INTEGER(unsigned=True), nullable=True, comment="开始运行时间")
    end_time = db.Column(INTEGER(unsigned=True), nullable=True, comment="结束时间")
    job_id = db.Column(db.String(255), nullable=True, default=0, comment="job的id")
    job_name = db.Column(db.String(255), nullable=True, comment="运行的调度任务名")
    switch = db.Column(INTEGER(unsigned=True), nullable=False, default=1,
                       comment="调度运行开关, 打开之后开始运行相关的任务调度 0:关闭 1:打开")

    # 任务状态
    READY = 0
    UNDERWAY = 1
    FINISHED = 2

    def __repr__(self):
        return '<SchedulerModel {}>'.format(self.name)
