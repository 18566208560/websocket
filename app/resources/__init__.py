from flask import current_app


def broadcast(room, msg):
    """通发redis发布订阅广播消息"""
    try:
        current_app.cli.publish(room, msg)
    except Exception as e:
        current_app.logger.exception(e)


def get_user_map(train):
    """当前实训的用户id与信息对应关系"""
    user_map = {}
    for team in train.teams:
        for user in team.users:
            user_map[user.id] = user.res_format_only(username=True, display_name=True, image=True)
    return user_map