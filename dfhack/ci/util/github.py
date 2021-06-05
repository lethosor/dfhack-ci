import re

def split_repo_url(url):
    parts = url.split('/')[-2:]
    if len(parts) < 2:
        raise ValueError('Invalid repository URL')
    parts[1] = re.sub(r'\.git$', '', parts[1])
    return tuple(parts)
