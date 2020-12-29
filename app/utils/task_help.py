import logging


from taskflow import task
from taskflow import engines

LOG = logging.getLogger("task")


class BaseTask(task.Task):
    """
    任务基类
    """

    def __init__(self, name=None, provides=None, requires=None, auto_extract=True, rebind=None,
            inject=None, ignore_list=None, revert_rebind=None, revert_requires=None, task_id=None,
            **kwargs):
        """
        :params kwargs:冗余参数,可以存放任务信息,然后更新任务状态或者告警等
        """
        super(BaseTask, self).__init__(name=name, provides=provides, requires=requires,
                auto_extract=auto_extract, rebind=rebind, inject=inject, ignore_list=ignore_list,
                revert_rebind=revert_rebind, revert_requires=revert_requires)
        self.task_id = task_id
        self.task_kwargs = kwargs


def _flow_transition(state, details):
    """
    流程过程信息
    """
    "REVERTED"
    identity = '...' if state == 'RUNNING' else '.'
    LOG.info('Flow [%s]: %s %s' %
             (details['flow_name'], state.lower(), identity))


def _task_transition(state, details):
    """
    任务过程信息
    """
    identity = '...' if state == 'RUNNING' else '.'
    if details.__contains__("task_name"):
        LOG.info('Task [%s]: %s %s' %
                 (details['task_name'], state.lower(), identity))
    if details.__contains__("retry_name"):
        LOG.info('RetryTask [%s]: %s %s' %
                (details['retry_name'], state.lower(), identity))


def run_serial_task_flow(flow, store):
    """
    串行运行任务
    :param flow: 任务流
    :param store: 任务execute函数的参数
    """
    eng = engines.load(flow, engines_conf={'engine': 'serial'}, store=store)
    eng.atom_notifier.register('*', _task_transition)
    eng.notifier.register('*', _flow_transition)
    eng.run()


class TaskError(Exception):
    pass
