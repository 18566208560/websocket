import os
import re
import time
import uuid
from datetime import datetime
from retrying import retry
from flask import current_app

# 允许上传的图片后缀
from app.utils.hash import file_md5

ALLOW_IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'bmp')

# 头像允许上传的大小, 800K
AVATAR_MAX_SIZE = 800 * 1024


def remove_file(path):
    """
    删除文件
    :param path: 文件绝对路径
    :return:
    """

    if path is not None and str(path).strip() != '':
        try:
            os.remove(path)
        except:
            pass


def remove_file_by_link(app, link, link_prefix='uploads'):
    """
    根据访问地址删除文件
    :param app: Flask app
    :param link: 页面访问地址
    :param link_prefix: 访问地址前缀
    :return:
    """

    upload_dir = app.config.get('UPLOAD_DIR')
    if upload_dir is None or upload_dir.strip() == '':
        return

    rel_path = link.replace('/{}/'.format(link_prefix.strip('/')), '', 1).strip('/')
    abs_path = os.path.join(upload_dir, rel_path)
    remove_file(abs_path)


def check_file_extension(file, allow_suffix=ALLOW_IMAGE_EXTENSIONS) -> bool:
    """
    检查图片后缀
    :param file: FileStorage 对象 (from werkzeug.datastructures import FileStorage)
    :return:
    """

    if file is None:
        return True
    if len(allow_suffix) == 0:
        return True

    # 后缀名不存在
    if len(file.filename.split('.')) < 2:
        return False

    ext = file.filename.split('.')[-1].lower()
    if ext in allow_suffix:
        return True

    return False


def check_avatar_size(file) -> bool:
    """
    检查头像文件大小
    :param file: FileStorage
    :return:
    """

    if file is None:
        return True

    file_len = get_sizes_by_list([file])
    if file_len > AVATAR_MAX_SIZE:
        return False

    return True


def get_sizes_by_list(files: list):
    """
    根据文件列表获取总大小
    :param files: [FileStorage]
    :return:
    """

    sizes = 0
    for file in files:
        file.seek(0, os.SEEK_END)
        sizes += file.tell()
        file.seek(0)  # 指针归零

    return sizes


def save_uploaded_image(app, file, name_prefix='', public_link=True, link_prefix='uploads'):
    """
    保存上传文件图片
    :param app: Flask app
    :param file: FileStorage 对象 (from werkzeug.datastructures import FileStorage)
    :param name_prefix: 文件名称前缀
    :param public_link: 是否返回访问地址
    :param link_prefix: 访问地址前缀
    :return: None or abspath or public link
    """

    # 检查是否有文件
    if file is None:
        return None

    upload_dir = app.config.get('UPLOAD_DIR')
    if upload_dir is None or upload_dir.strip() == '':
        raise Exception('App config [UPLOAD_DIR] missing')

    # 检查文件后缀名
    if not check_file_extension(file):
        raise Exception('Invalid image extension')

    # 按照日期创建目录
    current_date = datetime.today().strftime('%Y%m%d')

    file_ext = file.filename.split('.')[-1].lower()
    name_prefix = name_prefix or ''
    new_filename = '{}{}_{}.{}'.format(name_prefix, str(uuid.uuid4()), str(int(time.time())), file_ext)
    filepath = os.path.join(upload_dir, current_date, new_filename)

    # 检查目录是否存在
    if not os.path.isdir(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except Exception as e:
            raise e

    # 保存文件
    try:
        file.save(filepath)
    except Exception as e:
        raise e

    if public_link:
        return '/{}/{}/{}'.format(link_prefix.strip().strip('/'), current_date, new_filename)

    return filepath


def delete_train_img(app, train):
    """删除实训手册中的图片"""
    imgs = re.findall(r"!\[.*?\]\((.*?)\)", train.manual)
    for img in imgs:
        if img:
            remove_file_by_link(app, img)


def check_file_exist(app, img):
    """
    检测视频图片是否存在
    :param img:
    :return:
    """
    base_dir = app.config.get('BASE_DIR')
    if base_dir is None or base_dir.strip() == '':
        raise Exception('App config [BASE_DIR] missing')

    path = os.path.join(base_dir, img.strip('/'))
    if os.path.isfile(path):
        return True
    else:
        return False

def create_file(abs_file_path, file):
    """
    保存上传课程视频文件
    :param abs_file_path: 文件绝对路径
    :param file: FileStorage对象
    :return: 写入后指针位置
    """
    # 保存文件
    try:
        with open(abs_file_path, "wb") as f:
            f.write(file.stream.read())
            file_pos = f.tell()
    except Exception as e:
        raise e

    return file_pos


@retry(stop_max_attempt_number=3, stop_max_delay=50)
def append_file(abs_file_path, cur_size, file):
    """
    追加视频文件
    :param abs_file_path: 文件绝对路径
    :param cur_size:  当前位置
    :param file:  FileStorage对象
    :return: 写入后指针位置
    """
    if not os.path.exists(abs_file_path):
        raise Exception("file_not_found")
    try:
        with open(abs_file_path, "ab") as f:
            if f.tell() == cur_size:
                f.write(file.stream.read())
            file_pos = f.tell()
    except Exception as e:
        raise e

    return file_pos

def verify_file(abs_file_path, file_hash):
    """
    验证文件是否上传完成
    :param abs_file_path:  文件绝对路径
    :param file_hash: 文件hash
    :return:
    """
    if not os.path.exists(abs_file_path):
        raise Exception("file_not_found")
    if file_hash != file_md5(abs_file_path):
        raise Exception("file_error")



def upload_file(file_path, file_name, chunk, chunks, chunk_size, file, file_hash):
    """
    分片上传文件
    :param file_path: 文件绝对路径
    :param file_name: 文件名
    :param chunk:
    :param chunks:
    :param chunk_size:
    :param file:
    :param file_hash:
    :return:
    """
    abs_file_path = os.path.join(file_path, file_name)
    # 检查文件是否存在
    try:
        if os.path.exists(abs_file_path):
            # 向文件追加内容
            file_pos = append_file(abs_file_path, chunk * chunk_size, file)
            # 检查文件是否传完
            if chunk + 1 == chunks:
                status = verify_file(abs_file_path, file_hash)
                if status is None:
                    return True

            return file_pos

        else:

            # 保存文件返回pos
            file_pos = create_file(abs_file_path, file)

            # 检查文件是否完成
            if chunk + 1 == chunks:
                status = verify_file(abs_file_path, file_hash)
                if status is None:
                    return True

            return file_pos

    except Exception as e:
        # 　删除文件
        remove_file(abs_file_path)
        current_app.logger.exception(e)


def delete_train_video(app, paths):
    """删除录屏文件"""
    base_dir = app.config.get('BASE_DIR')
    for path in paths:
        abs_path = os.path.join(base_dir, path.strip("/"))
        remove_file(abs_path)


def remove_couse_video_by_links(app, links):
    file_dir = app.config.get('COURSE_VIDEO_DIR')
    for link in links:
        abs_file_path = os.path.join(file_dir, link.strip("/course"))
        remove_file(abs_file_path)
