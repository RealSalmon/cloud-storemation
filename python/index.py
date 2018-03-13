import http.client
import json
import logging
import os
import uuid
from urllib.parse import urlparse

import boto3

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())

MSG_EMPTY_PROPS = 'Empty resource properties'


def lambda_handler(event, context=None):

    response = {
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Status': 'SUCCESS'
    }

    # Make sure resource properties are there
    try:
        props = event['ResourceProperties']
    except KeyError:
        return send_fail(event, response, MSG_EMPTY_PROPS)

    # PhysicalResourceId is meaningless here, but CloudFormation requires it
    response['PhysicalResourceId'] = str(uuid.uuid4())

    # There is nothing to do for a delete request
    if event['RequestType'] == 'Delete':
        return send_response(event, response)

    data = {}
    try:
        data.update({
            p: get_parameters_by_path_as_list(p)
            for p in props.get('ParameterPathsAsList', list())
        })

        for p in props.get('ParameterPaths', list()):
            data.update(get_parameters_by_path(p))

        keys = props.get('Parameters')
        if keys:
            params = get_parameters(keys or list())
            data.update({k: params.get(k) for k in keys})

    except Exception as E:
        logger.error(str(E))
        return send_fail(event, response, str(E))

    response['Data'] = data
    return send_response(event, response)


def param_resp_to_params(response):
    list_params = {
        x['Name']: [y.strip() for y in x['Value'].split(',')]
        for x in response['Parameters']
        if x['Type'] == 'StringList'
    }
    params = {
        x['Name']: x['Value'] for x in response['Parameters']
        if x['Type'] != 'StringList'
    }
    params.update(list_params)

    return params


def get_parameters_by_path_as_list(path):
    response = boto3.client('ssm').get_parameters_by_path(Path=path)
    return [
        x['Value'] for x in response['Parameters'] if x['Type'] != 'StringList'
    ] + [
        [y.strip() for y in x['Value'].split(',')]
        for x in response['Parameters'] if x['Type'] == 'StringList'
    ]


def get_parameters_by_path(path):
    response = boto3.client('ssm').get_parameters_by_path(Path=path)
    return param_resp_to_params(response)


def get_parameters(names):
    if not len(names):
        return {}

    response = boto3.client('ssm').get_parameters(Names=names)
    return param_resp_to_params(response)


def send_response(request, response, status=None, reason=None):
    """ Send our response to the pre-signed URL supplied by CloudFormation
    If no ResponseURL is found in the request, there is no place to send a
    response. This may be the case if the supplied event was for testing.
    """
    if status is not None:
        response['Status'] = status

    if reason is not None:
        response['Reason'] = reason

    logger.debug("Response body is: %s", response)

    if 'ResponseURL' in request and request['ResponseURL']:
        url = urlparse(request['ResponseURL'])
        body = json.dumps(response)
        https = http.client.HTTPSConnection(url.hostname)
        logger.debug("Sending response to %s", request['ResponseURL'])
        https.request('PUT', url.path + '?' + url.query, body)
    else:
        logger.debug("No response sent (ResponseURL was empty)")

    return response


def send_fail(request, response, reason=None):
    if reason is not None:
        logger.error(reason)
    else:
        reason = 'Unknown Error - See CloudWatch log stream of the Lambda ' \
                 'function backing this custom resource for details'

    return send_response(request, response, 'FAILED', reason)
