#! /usr/bin/python

import os
import fcntl
import subprocess
import time
import sys

import git
import general

OPERATIONS = dict(
    mox_clone=general.init,
    mox_commit=git.commit,
    mox_pull=git.pull,
    mox_push=git.push,
    mox_delete=general.delete,
    mox_branch=git.branch,
    mox_merge=git.merge,
    mox_checkout=git.checkout
)


def run_instruction(details, i):
    d = details.copy()
    try:
        d['instruction'] = os.path.basename(i)
        d['project_name'] = os.path.basename(
            os.path.dirname(i)
        )
        d['git_path'] = os.path.join(
            d['git_root'],
            d['project_name']
        )
        d['dropbox_path'] = os.path.join(
            d['dropbox_root'],
            d['project_name']
        )
        with open(i, 'r') as fd:
            d['contents'] = fd.read().strip()
        os.remove(i)
        OPERATIONS[d['instruction']](d)
    except subprocess.CalledProcessError as cpe:
        path = os.path.join(d['dropbox_root'], 'error.txt')
        with open(path, 'w') as fd:
            fd.write(cpe.output)
    except Exception as e:
        path = os.path.join(d['dropbox_root'], 'error.txt')
        with open(path, 'w') as fd:
            fd.write(str(e))


def find_instruction(details):
    for parent, dirs, files in os.walk(details['dropbox_root']):
        for f in files:
            if f in OPERATIONS.keys():
                yield os.path.join(parent, f)


def dropbox_idle(details):
    o = subprocess.check_output([details['dropbox_cli'], 'status'])
    return o.strip() == 'Idle'


def load_config(lines):
    print lines
    details = {}
    for line in lines:
        k, v = line.split(':')
        details[k.strip()] = v.strip()
    return details


def main(config_path):
    print 'running, config in', config_path
    fd = open(config_path, 'r+')
    try:
        print 'getting lock'
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print 'loading config'
        details = load_config(fd.readlines())
        print details
        print 'waiting for idle dropbox'
        while not dropbox_idle(details):
            time.sleep(10)
        print 'finding instructions'
        for instruction in find_instruction(details):
            print 'running instruction', instruction
            run_instruction(details, instruction)
        print 'releasing lock'
        fcntl.lockf(fd, fcntl.LOCK_UN)
    except IOError as ioe:
        print 'there was an error:', ioe
        exit(1)
    finally:
        fd.close()

if __name__ == '__main__':
    main(sys.argv[1])
