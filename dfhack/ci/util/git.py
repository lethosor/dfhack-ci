import subprocess

def clone(url, destination, shallow=False, recursive=True):
    cmd = ['git', 'clone', url, destination]
    if shallow:
        cmd += ['--depth', '1']
    if recursive:
        cmd += ['--recurse-submodules']
        if shallow:
            cmd += ['--shallow-submodules']
    subprocess.check_call(cmd)
