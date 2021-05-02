import os.path

import dfhack.ci.util.git as git

def test_submodule_parse():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    gitmodules_path = os.path.join(test_dir, 'sample_gitmodules.txt')
    submodules = git.parse_gitmodules(gitmodules_path)
    assert submodules
    for s in submodules:
        assert s.key, s
        assert s.url, s
        assert s.path, s

    xml_submodule = next(s for s in submodules if s.path == 'library/xml')
    assert xml_submodule.key == 'library/xml'
    assert xml_submodule.url == '../../DFHack/df-structures.git'

    jsoncpp_submodule = next(s for s in submodules if s.path == 'depends/jsoncpp-sub')
    assert jsoncpp_submodule.key == 'depends/jsoncpp'
    assert jsoncpp_submodule.url == '../../DFHack/jsoncpp.git'

    expat_submodule = next(s for s in submodules if s.path == 'depends/libexpat')
    assert expat_submodule.key == 'depends/libexpat'
    assert expat_submodule.url == '../../DFHack/libexpat.git'
