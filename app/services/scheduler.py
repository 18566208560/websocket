import json
import os
import threading
from datetime import datetime
import time
import fcntl
import atexit
import logging
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from app.repositories.scheduler import SchedulerRepository
from app.models.scheduler import SchedulerModel

LOG = logging.getLogger("task")


def scheduler_init(app):
    """
    计划任务初始化
    使用文件锁保证在多进程下只有一个任务在运行
    :param app: Flask app
    :return:
    """
    base_dir = app.config.get('BASE_DIR')
    if base_dir is None:
        lock_file = '/tmp/scheduler.lock'
    else:
        lock_file = os.path.join(base_dir, 'logs', 'scheduler.lock')

    f = open(lock_file, 'wb')
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

        app.scheduler = BackgroundScheduler(timezone='Asia/Shanghai', executors=dict(default=ThreadPoolExecutor(100)))

        # 注册任务
        app.scheduler.add_job(func=update_status, trigger='cron', second='*/3', args=[app])
        app.scheduler.add_job(func=schedule_task, trigger='cron', second='*/3', args=[app])
        app.scheduler.start()

    except BlockingIOError:
        pass
    except Exception as e:
        LOG.exception(e)

    def unlock():
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()

    atexit.register(unlock)


def update_status(app):
    with app.app_context():
        try:
            LOG.info("update_status")
        except Exception as e:
            LOG.exception(e)

def recovery_snapshot(app, scheduler_id, params):
    with app.app_context():
        try:
            LOG.info("recovery_snapshot")
        except Exception as e:
            LOG.exception(e)

jobs = {"recovery_snapshot": recovery_snapshot}


def schedule_task(app):
    """
    任务调度,每秒在数据库获取任务进行apscheduler注册
    """
    with app.app_context():
        scheduler = app.scheduler
        try:
            # 获取需要注册的数据
            task_schedulers = SchedulerRepository.get_run_schedules()

            for task_scheduler in task_schedulers:

                func = jobs[task_scheduler.job_name]

                # 注册任务
                if task_scheduler.trigger == "interval":
                    job = scheduler.add_job(func, task_scheduler.trigger, minutes=task_scheduler.minutes,
                                            start_date=datetime.fromtimestamp(task_scheduler.start_time),
                                            args=[app, task_scheduler.id, task_scheduler.params])
                elif task_scheduler.trigger == "date":
                    job = scheduler.add_job(func, task_scheduler.trigger,
                                            run_date=datetime.fromtimestamp(task_scheduler.start_time),
                                            args=[app, task_scheduler.id, task_scheduler.params])

                # 将apscheduler的id写入对应的任务数据行
                SchedulerRepository.update_scheduler(task_scheduler, job_id=job.id, status=SchedulerModel.UNDERWAY)
                LOG.info("add_job: %s - %s" % (task_scheduler.name, job.id))

            # 移除不需要运行的job
            task_schedulers = SchedulerRepository.get_remove_schedules()
            for task_scheduler in task_schedulers:
                job = scheduler.get_job(task_scheduler.job_id)
                if job:
                    job.remove()
                    LOG.info("remove_job: %s - %s" % (task_scheduler.name, job.id))

        except Exception as e:
            LOG.exception(e)
