import os
from typing import BinaryIO
from app.helpers.aws_services import s3_client

bucket = os.getenv('BUCKET_NAME', 'amzon-s3-api-app')
region = os.getenv('S3_REGION', 'ap-south-1')

def upload_bytes_to_s3(data: bytes, key: str, content_type: str = 'application/octet-stream') -> str:
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentType=content_type
    )
    region = os.getenv('S3_REGION', 'ap-south-1')
    return get_s3_url(bucket, key, region)

def upload_file_to_s3(file_obj: BinaryIO, key: str, content_type: str = 'application/octet-stream') -> str:
    s3_client.upload_fileobj(
        file_obj,
        bucket,
        key,
        ExtraArgs={'ContentType': content_type}
    )
    region = os.getenv('S3_REGION', 'ap-south-1')
    return get_s3_url(bucket, key, region)

def delete_from_s3(bucket: str, key: str) -> bool:
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return True
    except Exception as e:
        print(f"Error deleting from S3: {e}")
        return False

def get_s3_url(bucket: str, key: str, region: str) -> str:
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"