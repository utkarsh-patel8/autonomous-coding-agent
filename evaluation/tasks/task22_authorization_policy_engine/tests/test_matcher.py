from authz.matcher import path_matches

def test_star_matches_one_segment_only():
    assert path_matches('/projects/*/settings','/projects/p1/settings')
    assert not path_matches('/projects/*/settings','/projects/team/p1/settings')

def test_double_star_matches_zero_or_many_segments():
    assert path_matches('/projects/**','/projects')
    assert path_matches('/projects/**','/projects/p1')
    assert path_matches('/projects/**','/projects/p1/files/a.txt')
