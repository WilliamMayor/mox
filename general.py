import os
import stat
import shutil
import subprocess

import git


def __remove_readonly(fn, path, excinfo):
    if fn is os.rmdir:
        os.chmod(path, stat.S_IWRITE)
        os.rmdir(path)
    elif fn is os.remove:
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)


def delete(details):
    if details['contents'] == details['project_name']:
        shutil.rmtree(
            details['dropbox_path'],
            ignore_errors=False,
            onerror=__remove_readonly
        )
        shutil.rmtree(
            details['git_path'],
            ignore_errors=False,
            onerror=__remove_readonly
        )


def ls(directory):
    output = subprocess.check_output(
        ['ls', directory],
        stderr=subprocess.STDOUT
    )
    return output.split('\n')


def init(details):
    before = set(ls(details['git_root']))
    subprocess.check_output(
        ['git', 'clone', details['contents']],
        cwd=details['git_root'],
        stderr=subprocess.STDOUT
    )
    after = set(ls(details['git_root']))
    new = list(after - before)[0]
    git_path = os.path.join(details['git_root'], new)
    dropbox_path = os.path.join(details['dropbox_root'], new)
    os.mkdir(dropbox_path)
    git.__copy(git_path, dropbox_path)
    incrontab = subprocess.check_output(
        ['incrontab', '-l']
    )
    with open(details['incron'], 'w') as fd:
        fd.write(incrontab)
        fd.write('\n')
        fd.write(dropbox_path)
        fd.write(' IN_CLOSE_WRITE,IN_CREATE,IN_MOVED_TO python ')
        fd.write(details['mox_path'])
        fd.write(' ')
        fd.write(details['config_path'])
    subprocess.check_output(
        ['incrontab', details['incron']],
        stderr=subprocess.STDOUT
    )
