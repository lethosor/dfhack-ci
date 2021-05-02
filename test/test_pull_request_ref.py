import pytest

from dfhack.ci.util.github_parse import PullRequestRef

SAMPLE_WEB_URL = 'https://github.com/DFHack/dfhack/pull/43'
SAMPLE_API_URL = 'https://api.github.com/repos/DFHack/dfhack/pulls/1777'

def test_url_pattern_match():
    match = PullRequestRef.WEB_URL_PATTERN.match(SAMPLE_WEB_URL)
    assert match is not None
    assert match.group('repo_owner') == 'DFHack'
    assert match.group('repo_name') == 'dfhack'
    assert match.group('pr_number') == '43'

def test_from_url():
    ref = PullRequestRef.from_url(SAMPLE_WEB_URL)
    assert ref.repo_owner == 'DFHack'
    assert ref.repo_name == 'dfhack'
    assert ref.pr_number == 43

def test_from_api_url():
    ref = PullRequestRef.from_api_url(SAMPLE_API_URL)
    assert ref.repo_owner == 'DFHack'
    assert ref.repo_name == 'dfhack'
    assert ref.pr_number == 1777

def test_from_text_ref():
    ref = PullRequestRef.from_text_ref('DFHack/dfhack#123')
    assert ref.repo_owner == 'DFHack'
    assert ref.repo_name == 'dfhack'
    assert ref.pr_number == 123

def test_from_text_ref_default_name():
    ref = PullRequestRef.from_text_ref('lethosor#123', default_repo_name='dfhack')
    assert ref.repo_owner == 'lethosor'
    assert ref.repo_name == 'dfhack'
    assert ref.pr_number == 123

def test_from_text_ref_missing_name():
    with pytest.raises(ValueError) as excinfo:
        PullRequestRef.from_text_ref('lethosor#123')
    assert 'missing repo name' in str(excinfo.value).lower()

def test_from_text_ref_default_owner():
    ref = PullRequestRef.from_text_ref('#456', default_repo_owner='foo', default_repo_name='dfhack')
    assert ref.repo_owner == 'foo'
    assert ref.repo_name == 'dfhack'
    assert ref.pr_number == 456

def test_from_text_ref_missing_owner():
    with pytest.raises(ValueError) as excinfo:
        PullRequestRef.from_text_ref('#123', default_repo_name='x')
    assert 'missing repo owner' in str(excinfo.value).lower()

def test_from_description():
    desc = """
    This is a test PR
    description.

    Requires: DFHack/dfhack#123
    needs lethosor/dfhack#890, https://github.com/DFHack/scripts/pull/276, a/b#1
    """.strip()
    refs = PullRequestRef.all_from_description(desc)
    assert refs == [
        PullRequestRef(repo_owner='DFHack', repo_name='dfhack', pr_number=123),
        PullRequestRef(repo_owner='lethosor', repo_name='dfhack', pr_number=890),
        PullRequestRef(repo_owner='DFHack', repo_name='scripts', pr_number=276),
        PullRequestRef(repo_owner='a', repo_name='b', pr_number=1),
    ]


def test_from_description_errors():
    desc = """
    foo.

    Uses bar#123, foo/baz#4
    """.strip()

    refs = PullRequestRef.all_from_description(desc, ignore_errors=True)
    assert refs == [
        PullRequestRef(repo_owner='foo', repo_name='baz', pr_number=4),
    ]

    with pytest.raises(ValueError) as excinfo:
        refs = PullRequestRef.all_from_description(desc)
    assert 'missing repo name' in str(excinfo.value).lower()
