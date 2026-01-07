import boto3
import os
from dotenv import load_dotenv

load_dotenv()

aws_session = boto3.Session( 
    aws_access_key_id=os.getenv('ACCESS_KEY_ID'), 
    aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'), 
    region_name=os.getenv('S3_REGION') 
)

ses_client = aws_session.client('ses')
sqs_client = aws_session.client('sqs')
s3_client = aws_session.client('s3')