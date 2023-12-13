![cloud-storemation](https://github.com/realsalmon/cloud-storemation/actions/workflows/main.yml/badge.svg)
# CloudStoremation

## A custom resource for CloudFormation that enhances integration with AWS Systems Manager Parameter Store

Better README coming "soon".

### Install
1. Create new stack with cloud-formation/cloud-formation.yml
2. Update Lambda function with python/index.py
3. Try it with the example template at cloud-formation/example.yml

### Usage
```yaml
CloudStoremation:
  Type: "Custom::CloudStoremation"
  Version: "1.0"
  Properties:
    ServiceToken: !Ref "CloudStormationKey"
    ParameterPathsAsList: # key, list for each member for each item in path
      - ...
      - ...
    ParameterPaths:  # key, value for each member for each item in path
      - ...
      - ...
    Parameters: # key, value for each member
      - ...
    ParameterRando: !Ref "ParameterRandoKey" # optional but recommended...used to force refresh
#
#
!GetAtt ["CloudStormation", <key>]
```
