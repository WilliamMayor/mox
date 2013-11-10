import subprocess
import os
import shutil


def __run(details, args):
    subprocess.check_output(
        args,
        cwd=details['git_path'],
        stderr=subprocess.STDOUT
    )


def __empty(directory):
    for f in os.listdir(directory):
        if f != '.git':
            try:
                os.remove(os.path.join(directory, f))
            except:
                shutil.rmtree(os.path.join(directory, f))


def __copy(src, dest):
    __empty(dest)
    for f in os.listdir(src):
        if f != '.git':
            try:
                shutil.copy(os.path.join(src, f), os.path.join(dest, f))
            except:
                shutil.copytree(os.path.join(src, f), os.path.join(dest, f))


def commit(details):
    __copy(
        details['dropbox_path'],
        details['git_path']
    )
    __run(
        details,
        ['git', 'add', details['git_path']]
    )
    __run(
        details,
        ['git', 'commit', '-m', details['contents']]
    )


def push(details):
    __run(
        details,
        ['git', 'push']
    )


def pull(details):
    __run(
        details,
        ['git', 'pull']
    )
    __copy(
        details['git_path'],
        details['dropbox_path']
    )


def branch(details):
    __run(
        details,
        ['git', 'branch', details['contents']]
    )
    __run(
        details,
        ['git', 'push', 'origin', details['contents']]
    )
    checkout(details)


def checkout(details):
    __run(
        details,
        ['git', 'checkout', details['contents']]
    )
    __copy(
        details['git_path'],
        details['dropbox_path']
    )


def merge(details):
    a, b = details['contents'].split('\n')
    __run(
        details,
        ['git', 'checkout', b]
    )
    __run(
        details,
        ['git', 'merge', a]
    )
    __copy(
        details['git_path'],
        details['dropbox_path']
    )
