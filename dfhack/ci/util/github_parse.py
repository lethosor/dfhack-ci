import contextlib
import re

class PullRequestRef:
    WEB_URL_PATTERN = re.compile(r'https?://(.*?\.)?github\.com/(?P<repo_owner>[a-z0-9-_]+)/(?P<repo_name>[a-z0-9-_]+)/pull/(?P<pr_number>\d+)', flags=re.IGNORECASE)
    API_URL_PATTERN = re.compile(r'https?://api\.github\.com/repos/(?P<repo_owner>[a-z0-9-_]+)/(?P<repo_name>[a-z0-9-_]+)/pulls/(?P<pr_number>\d+)', flags=re.IGNORECASE)
    TEXT_REF_PATTERN = re.compile(r'((?P<repo_owner>[a-z0-9-_]+)(/(?P<repo_name>[a-z0-9-_]+))?)?#(?P<pr_number>\d+)', flags=re.IGNORECASE)

    DESCRIPTION_PATTERN = re.compile(r'(^|\n)\s*(requires|needs|depends\s+on|uses)[\s:]*(?P<content>.+)', flags=re.IGNORECASE)

    def __init__(self, repo_owner, repo_name, pr_number):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_number = int(pr_number)

    def __eq__(self, other):
        return (
            self.repo_owner == other.repo_owner and
            self.repo_name == other.repo_name and
            self.pr_number == other.pr_number
        )

    def __repr__(self):
        return '<PullRequestRef: %s/%s#%d>' % (self.repo_owner, self.repo_name, self.pr_number)

    @classmethod
    def from_url(cls, url):
        match = cls.WEB_URL_PATTERN.match(url)
        if match is None:
            raise ValueError('Invalid web URL: %r' % url)
        return cls(**match.groupdict())

    @classmethod
    def from_api_url(cls, url):
        match = cls.API_URL_PATTERN.match(url)
        if match is None:
            raise ValueError('Invalid API URL: %r' % url)
        return cls(**match.groupdict())

    @classmethod
    def from_text_ref(cls, ref, default_repo_owner=None, default_repo_name=None):
        match = cls.TEXT_REF_PATTERN.match(ref)
        if match is None:
            raise ValueError('Invalid PR text reference: %r' % ref)

        kwargs = match.groupdict()

        if kwargs['repo_owner'] is None:
            if default_repo_owner is not None:
                kwargs['repo_owner'] = default_repo_owner
            else:
                raise ValueError('Missing repo owner and no default provided: %r' % ref)

        if kwargs['repo_name'] is None:
            if default_repo_name is not None:
                kwargs['repo_name'] = default_repo_name
            else:
                raise ValueError('Missing repo name and no default provided: %r' % ref)

        return cls(**kwargs)

    @classmethod
    def all_from_description(cls, desc, default_repo_owner=None, default_repo_name=None, ignore_errors=False):
        @contextlib.contextmanager
        def error_wrapper():
            try:
                yield
            except ValueError:
                if not ignore_errors:
                    raise

        matches = []  # pairs of (index, PullRequestRef)
        for match in cls.DESCRIPTION_PATTERN.finditer(desc):
            content = match.group('content')
            for match in cls.WEB_URL_PATTERN.finditer(content):
                with error_wrapper():
                    matches.append((match.start(), cls.from_url(match.group(0))))
            for match in cls.TEXT_REF_PATTERN.finditer(content):
                with error_wrapper():
                    matches.append((match.start(), cls.from_text_ref(
                        match.group(0),
                        default_repo_owner=default_repo_owner,
                        default_repo_name=default_repo_name,
                    )))

        # sort matches by their index, then return just the PullRequestRef
        matches.sort(key=lambda pair: pair[0])
        return [m[1] for m in matches]

    def _format(self, format_spec):
        return format_spec.format(**{k: getattr(self, k) for k in dir(self)})

    def as_url(self):
        return self._format('https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}')

    def as_api_url(self):
        return self._format('https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}')

    def as_text_ref(self):
        return self._format('{repo_owner}/{repo_name}#{pr_number}')
