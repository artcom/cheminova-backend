import os

from boto3.session import Session
from botocore.client import Config


def get_bucket(s3_alias: str, bucket_name: str):
    """
    Return the S3 bucket for the given profile of the AWS config at S3_CONFIG_PATH.

    Endpoint, region and addressing style are read from the profile.
    """
    os.environ["AWS_CONFIG_FILE"] = os.environ["S3_CONFIG_PATH"]
    session = Session(profile_name=s3_alias)
    s3 = session.resource("s3", config=Config(signature_version="s3v4"))
    return s3.Bucket(bucket_name)
