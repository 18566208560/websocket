import os
import traceback

def save_split_file(request, task_id, chunk, save_dir):
    """
    保存前端上传的分片文件
    :param task_id: 文件唯一标识符
    :param chunk: 该分片在所有分片中的序号
    :param save_dir: 保存的路径
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    upload_file = request.files['file']
    filename = '%s%s' % (task_id, chunk)
    upload_path = os.path.join(save_dir, filename)
    upload_file.save(upload_path)
    return True


def merge_split_file(filename, task_id, source_dir, save_dir):
    """
    合并前端上传的分片文件
    :param filename: 文件名称
    :param task_id: 件唯一标识符
    :param source_dir: 分片文件的保存路径
    :param save_dir: 最终文件保存的路径
    """
    chunk = 0
    target_file_path = os.path.join(save_dir, filename)
    with open(target_file_path, 'wb') as target_file:
        while True:
            try:
                filename = os.path.join(source_dir, "%s%d"%(task_id, chunk))
                source_file = open(filename, 'rb')
                target_file.write(source_file.read())
                source_file.close()
                chunk += 1
            except IOError as e:
                traceback.print_exc()
                break
            os.remove(filename)
    return True
