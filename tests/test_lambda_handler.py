import boto3
import index
from moto import mock_ssm
from test_get_parameters import setup_parameters, param_is_expected
from test_get_parameters import params, params_as_list, params_as_path


def get_event():
    return {
        "StackId": "12345",
        "RequestId": "ohai!",
        "LogicalResourceId": "best-logical-resource-evar",
        "RequestType": "Create",
        "ResourceProperties": {
            "ParameterPathsAsList": [
                "/path/as/list1",
                "/path/as/list2",
            ],
            "ParameterPaths": [
                "/path/as/path1",
                "/path/as/path2"
            ],
            "Parameters": [
                "/params/param1",
                "/params/param2",
                "/params/bleh"
            ]
        }
    }


@mock_ssm
def test_empty_params():
    setup_parameters()
    event = get_event()
    del event['ResourceProperties']

    response = index.lambda_handler(event)
    assert 'Status' in response
    assert response['Status'] == 'FAILED'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert response['RequestId'] == event['RequestId']
    assert response['Reason'] == index.MSG_EMPTY_PROPS


@mock_ssm
def test_delete():
    setup_parameters()
    event = get_event()
    event['RequestType'] = 'Delete'
    response = index.lambda_handler(event)
    assert response['Status'] == 'SUCCESS'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert response['RequestId'] == event['RequestId']


@mock_ssm
def test_success_all():

    setup_parameters()
    event = get_event()
    response = index.lambda_handler(event)
    data = response['Data']

    assert response['Status'] == 'SUCCESS'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert len(response['PhysicalResourceId']) > 0
    assert response['RequestId'] == event['RequestId']

    for i in [params, params_as_path]:
        for k, v in i.items():
            assert param_is_expected(data[k], v)

    for k in event['ResourceProperties']['ParameterPathsAsList']:
        expected = [
            y[0] if y[1] != 'StringList' else [z.strip() for z in y[0].split(',')]
            for x, y in params_as_list.items() if x.startswith(k)
        ]
        assert len(expected) == len(data[k])
        for v in expected:
            assert v in data[k]


@mock_ssm
def test_missing_as_list():
    setup_parameters()
    event = get_event()
    event['ResourceProperties']= {'ParameterPathsAsList':  ['/no/such/path']}
    response = index.lambda_handler(event)
    assert response['Status'] == 'SUCCESS'
    assert response['Data']['/no/such/path'] == []


@mock_ssm
def test_missing_as_path():
    setup_parameters()
    event = get_event()
    event['ResourceProperties']= {'ParameterPaths':  ['/no/such/path']}
    response = index.lambda_handler(event)
    assert response['Status'] == 'SUCCESS'
    assert response['Data'] == {}


@mock_ssm
def test_missing_param():
    setup_parameters()
    event = get_event()
    event['ResourceProperties']= {'Parameters':  ['/no/such/path']}
    response = index.lambda_handler(event)
    assert response['Status'] == 'SUCCESS'
    assert response['Data']['/no/such/path'] is None
