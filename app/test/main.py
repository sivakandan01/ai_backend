from helpers.aws_services import ses_client, sqs_client
import os
from dotenv import load_dotenv
import json

load_dotenv()

class Aws_services:
    @staticmethod
    async def ses_service():

        ses_client.send_email(
            Source=os.getenv("SOURCE_EMAIL"),
            Destination={
                "ToAddresses": [os.getenv("DESTINATION_EMAIL")]
            },
            Message={
                "Subject": { "data": "" },
                "Body": {
                    "Text": { "data": "" }
                }
            }
        )

    @staticmethod
    async def sqs_service():

        payload = {
            "user_id": "123",
            "message": "Permission Changed"
        }

        sqs_client.send_message(
            Query_url=os.getenv("QUERY_URL"),
            MessageBody=json.dumps(payload)
        )