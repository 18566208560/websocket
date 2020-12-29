import time
import json

from app.models import db
from app.models.scheduler import SchedulerModel


class SchedulerRepository(object):

    @staticmethod
    def create_scheduler(name, job_name, status=0, params={}, trigger="date", minutes=0, start_time=0, end_time=0):
        try:
            scheduler = SchedulerModel()
            scheduler.name = name
            scheduler.job_name = job_name
            scheduler.status = status
            scheduler.params = json.dumps(params)
            scheduler.create_time = int(time.time())
            scheduler.trigger = trigger
            scheduler.minutes = minutes
            scheduler.start_time = start_time + 5
            scheduler.end_time = end_time

            db.session.add(scheduler)
            db.session.commit()
            return scheduler
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_scheduler(scheduler, **kwargs):
        try:
            if kwargs.__contains__("params"):
                kwargs["params"] = json.dumps(kwargs["params"])
            SchedulerModel.query.filter(SchedulerModel.id == scheduler.id).update(kwargs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_schedule(id=None, name=None):
        id_filter = SchedulerModel.id == id if id != None else True
        name_filter = SchedulerModel.name == name if name != None else True
        return SchedulerModel.query \
            .filter(id_filter) \
            .filter(name_filter) \
            .first()

    @staticmethod
    def get_run_schedules():
        query = SchedulerModel.query \
            .filter_by(status=0) \
            .filter(SchedulerModel.switch == 1)
        return query.all()

    @staticmethod
    def get_remove_schedules():

        query = SchedulerModel.query \
            .filter_by(status=1) \
            .filter(SchedulerModel.switch == 0)
        return query.all()

    @staticmethod
    def update_schedulers(filters, update_data):
        try:
            SchedulerModel.query.filter_by(**filters).update(update_data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
