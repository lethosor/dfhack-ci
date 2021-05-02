import collections
import re
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

SubmoduleInfo = collections.namedtuple('SubmoduleInfo', (
    'key',
    'path',
    'url',
))

def parse_gitmodules(file_path):
    raw_entries = {}
    current_key = None
    entry_start_pattern = re.compile(r'\[submodule\s+"(?P<key>.+)"\]')
    setting_pattern = re.compile(r'(?P<name>\S+)\s*=\s*(?P<value>\S+)')
    with open(file_path, 'r') as f:
        for line in f.readlines():
            match = entry_start_pattern.search(line)
            if match is not None:
                key = match.group('key')
                if key not in raw_entries:
                    raw_entries[key] = {}
                    current_key = key
                else:
                    raise ValueError('Duplicate submodule entry: %r' % key)
                continue
            match = setting_pattern.search(line)
            if match is not None:
                if current_key is None:
                    raise ValueError('Line before submodule definition: %r' % line)
                name, value = match.group('name'), match.group('value')
                if name in raw_entries[current_key]:
                    raise ValueError('Duplicate submodule setting: %r = %r' % (name, value))
                raw_entries[current_key][name] = value
                continue

    return [
        SubmoduleInfo(
            key=key,
            path=settings.get('path'),
            url=settings.get('url'),
        ) for key, settings in raw_entries.items()
    ]
