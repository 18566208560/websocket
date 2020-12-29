from flask import current_app
from app.models.contest import ContestModel
from app.models.tq30 import TrainModel


def get_train_id(contest_id=None):
    """
    获取当前激活比赛关联的实训
    :return: int or str
    """
    try:
        fields = {"deleted_at": 0, "active": 1}
        if contest_id:
            fields["id"] = contest_id
            fields.pop("active")
        contest = ContestModel.get_model_by_fields(**fields)
        train_id = contest.subjects[0].train_id
        train = TrainModel.get_model_by_fields(id=train_id, deleted_at=0, train_status=2)
        if not train:
            return "train_not_found"
        return train
    except AttributeError as e:
        current_app.logger.exception(e)
        return "active_contest_not_found"
    except IndexError as e:
        current_app.logger.exception(e)
        return "subject_not_found"
    except Exception as e:
        current_app.logger.exception(e)
        return "system_error"

def get_train_maps(train):
    """获取team_id-scene_id 对应关系， host_id-host_ip对应关系"""
    team_scene_map = {}
    host_id_ip_map = {}
    for host in train.train_hosts:
        team_scene_map[host.scene_id] = host.team_id
        team_scene_map[host.team_id] = host.scene_id

        host_id_ip_map[host.id] = host.host_ip
        host_id_ip_map[host.host_ip] = host.id

    return team_scene_map, host_id_ip_map
