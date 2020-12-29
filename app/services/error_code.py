"""
错误码说明
第1~2位: 01 ~ 99, 表示产品, 02 -> 天穹
第3~5位: 001 ~ 999, 表示项目组, 001-099 为虚拟化预留, 100-199 WEB接口预留, 100 -> WEB接口
第6~8位: 001 ~ 999, 表示功能/模块
第9~11位: 001~999, 表示具体错误
这里只需定义 6~8 及 9~11 位即可
"""
error_code_list = {
    # 无错误
    'ok': '000000|',

    # 系统错误 001
    'error': '001001|',  # 自定义错误
    'system_error': '001002|系统错误',
    'not_found': '001003|404未找到',
    'permission_denied': '001004|权限不足',
    'param_error': '001005|参数错误',
    'invalid_file_extension': '001006|文件类型错误',
    'avatar_image_oversize': '001007|头像文件超出尺寸',
    'config_miss': '001008|配置缺失',

    # 数据库 002
    'row_not_found': '002001|记录未找到',
    'create_row_fail': '002002|创建记录失败',
    'update_row_fail': '002003|更新记录失败',
    'delete_row_fail': '002004|删除记录失败',
    'row_exists': '002005|记录已存在',

    # 用户 003
    'token_missing': '003001|缺少Token',
    'invalid_token': '003002|您的登陆已过期，请重新登录',
    'invalid_auth_params': '003003|用户名或密码错误',
    'invalid_old_password': '003004|用户密码错误',
    'invalid_new_password': '003005|用户新密码错误',
    'team_not_found': '003006|团队未找到',
    'student_not_found': '003007|选手未找到',
    'teacher_not_found': '003008|教师未找到',
    'log_not_found': '003009|日志未找到',
    'invalid_username': '003010|用户名格式错误',
    'invalid_display_name': '003011|姓名格式错误',
    'same_username_password': '003012|密码不能与用户名相同',
    'invalid_password': '003013|密码格式错误',
    'invalid_company': '003014|公司名格式错误',
    'invalid_team_name': '003015|团队名称格式错误',
    'user_exists': '003016|用户已存在',
    'create_user_fail': '003017|创建用户失败',
    'user_not_found': '003018|用户不存在',
    'update_user_fail': '003019|更新用户失败',
    'delete_user_fail': '003020|删除用户失败',
    'team_exists': '003021|团队已存在',
    'create_team_fail': '003022|创建团队失败',
    'update_team_fail': '003023|更新团队失败',
    'delete_team_fail': '003024|删除团队失败',
    'update_profile_fail': '003025|更新信息失败',
    'user_login_fail': '003026|用户登录失败',
    'user_logout_fail': '003027|用户退出失败',
    'delete_user_has_train': '003028|学员与实训关联',
    'delete_user_has_team': '003029|学员与团队关联',
    'delete_team_has_train': '003030|团队与实训关联',
    'invalid_image': '003031|无效的头像',
    'duplicate_username': '003032|用户名重复',
    'duplicate_display_name': '003033|登录名重复',
    'invalid_profile_id': '003034|无效的头像id',
    'profile_not_found': '003035|头像未找到',
    'profile_delete_error': '003036|头像删除失败',
    'captcha_error': '003037|验证码错误',
    'member_full': '003038|团队成员已满',
    'attack_member_full': '003039|团队攻防成员已满',
    'ai_member_full': '003040|团队ai成员已满',
    'join_team_error': '003041|加入团队失败',
    'joined_team': '003042|已加入团队',
    'joined_other_team': '003043|已加入其它团队',
    'contest_not_start': '003044|比赛未开始，暂时无法登陆',

    # 比赛005
    'contest_not_found': '005001|比赛未找到',
    'train_not_found': '005002|关联实训未找到',
    'contest_create_failed': '005003|比赛创建失败',
    'contest_update_failed': '005004|比赛更新失败',
    'contest_delete_failed': '005005|比赛删除失败',
    'contest_started': '005006|比赛已开始',
    'contest_finished': '005007|比赛已结束',
    'cannot_pause': '005008|比赛当前状态不能暂停',
    'contest_not_pause': '005009|比赛未暂停',
    'cannot_delete_by_status': '005010|比赛已开始不能删除',
    'active_contest_not_found': '005011|激活比赛未找到',
    'subject_not_found': '005012|赛题未找到',
    'starting_cannot_edit': '005013|进行中比赛不能修改',
    'contest_name_repeat': '005014|比赛名称重复',

    # flag 006
    'flag_sys_error': '006001|flag提交失败',
    'flag_error': '006002|flag错误',
    'flag_exists': '006003|flag已提交',
    'invalid_user': '006004|无效用户',
    'cannot_post_flag': '006005|进行中的比赛才能提交flag',
    'insert_flag_failed': '006006|插入flag失败',

    # attack_data
    'file_not_found': '007001|样本文件未找到',

    # 资源切换
    'dst_team_error': '008001|目标团队错误',
    'src_team_error': '008002|源团队错误',
    'switch_failed': '008003|资源切换失败',

}
