import torch
import boto3
import os

accesskey = os.environ.get("AWS_ACCESS_KEY_ID")
secretkey = os.environ.get("AWS_SECRET_ACCESS_KEY")
boto3.setup_default_session(region_name="us-west-2")
client = boto3.client(
    "lambda",
    aws_access_key_id=accesskey,
    aws_secret_access_key=secretkey,
)


def checkgpu():
    a = torch.cuda.is_available()
    print(a)
    for i in range(torch.cuda.device_count()):
        print(torch.cuda.get_device_properties(i).name)
    return a
