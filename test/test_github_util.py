import dfhack.ci.util.github as github

def test_split_repo_url():
    assert github.split_repo_url('https://github.com/DFHack/dfhack') == ('DFHack', 'dfhack')

def test_split_repo_url_relative():
    assert github.split_repo_url('../../DFHack/df-structures') == ('DFHack', 'df-structures')

def test_split_repo_url_git():
    assert github.split_repo_url('git://github.com/DFHack/stonesense.git') == ('DFHack', 'stonesense')

def test_split_repo_url_name():
    assert github.split_repo_url('DFHack/scripts') == ('DFHack', 'scripts')
