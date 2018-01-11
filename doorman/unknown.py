import json
import boto3
import requests
import hashlib
import os
from urllib.parse import parse_qs

bucket_name = os.environ['BUCKET_NAME']
slack_token = os.environ['SLACK_API_TOKEN']
slack_channel_id = os.environ['SLACK_CHANNEL_ID']
rekognition_collection_id = os.environ['REKOGNITION_COLLECTION_ID']


def unknown(event, context):
    key = event['Records'][0]['s3']['object']['key']

    data = {
        "channel": slack_channel_id,
        "text": "I don't know who this is, can you tell me?",
        "attachments": [
            {
                "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, key),
                "fallback": "Nope?",
                "callback_id": key,
                "attachment_type": "default",
                "actions": [{
                        "name": "username",
                        "text": "Select a username...",
                        "type": "select",
                        "data_source": "users"
                    },
                    {
                        "name": "discard",
                        "text": "Ignore",
                        "style": "danger",
                        "type": "button",
                        "value": "ignore",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Are you sure you want to ignore and delete this image?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            }
        ]
    }
    print(data)
    foo = requests.post("https://slack.com/api/chat.postMessage", headers={'Content-Type':'application/json;charset=UTF-8', 'Authorization': 'Bearer %s' % slack_token}, json=data)

    print(foo.json())
