import boto3
import index
from moto import mock_ssm

params_as_list = {
    '/path/as/list1/val1': ('value 1', 'String'),
    '/path/as/list1/val2': ('value 2', 'String'),
    '/path/as/list1/bleh': ('yadda1, yadda2, yadda3', 'StringList'),
    '/path/as/list2/val1': ('another value 1', 'String'),
    '/path/as/list2/val2': ('another value 2', 'String'),
    '/path/as/list2/bleh': ('another yadda1, another yadda2, another yadda3',
                            'StringList')
}
params_as_path = {
    '/path/as/path1/val1': ('path value 1', 'String'),
    '/path/as/path1/val2': ('path value 2', 'String'),
    '/path/as/path1/bleh': ('path yadda1, path yadda2, path yadda3',
                            'StringList'),
    '/path/as/path2/val1': ('another path value 1', 'String'),
    '/path/as/path2/val2': ('another path value 2', 'String'),
    '/path/as/path2/bleh': (
        'another path yadda1, another path yadda2, another path yadda3',
        'StringList'
    )
}
params = {
    '/params/param1': ('param value 1', 'String'),
    '/params/param2': ('param value 2', 'String'),
    '/params/bleh': (
        'param value yadda1, param value yadda2, param value yadda3',
        'StringList'
    )
}


def param_is_expected(actual, xtuple):
    if xtuple[1] == 'String':
        return actual == xtuple[0]
    elif xtuple[1] == 'StringList':
        return actual == [x.strip() for x in xtuple[0].split(',')]


def setup_parameters():
    ssm = boto3.client('ssm')
    for x in [params, params_as_path, params_as_list]:
        for p, t in x.items():
            ssm.put_parameter(Name=p, Value=t[0], Type=t[1])


@mock_ssm
def test_get_parameters_by_path_as_list():
    setup_parameters()
    path = '/path/as/list1'
    lparams = index.get_parameters_by_path_as_list(path)
    assert len(lparams) is 3
    assert 'value 1' in lparams
    assert 'value 2' in lparams
    assert ['yadda1', 'yadda2', 'yadda3'] in lparams


@mock_ssm
def test_get_parameters_by_path():
    setup_parameters()
    path = '/path/as/path1'
    lparams = index.get_parameters_by_path(path)
    assert len(lparams) is 3
    expected = {x:y for x,y in params_as_path.items() if x.startswith(path)}
    for k, v in expected.items():
        assert param_is_expected(lparams[k], v)


@mock_ssm
def test_get_parameters():
    setup_parameters()
    lparams = index.get_parameters(list(params.keys()))
    assert len(lparams) is 3
    for k, v in params.items():
        assert param_is_expected(lparams[k], v)
