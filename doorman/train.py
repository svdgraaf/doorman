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


def train(event, context):
    # print(event['body'])
    data = parse_qs(event['body'])
    data = json.loads(data['payload'][0])
    print(data)
    key = data['callback_id']

    # if we got a discard action, send an update first, and then remove the referenced image
    if data['actions'][0]['name'] == 'discard':
        message = {
            "text": "Ok, I ignored this image",
            "attachments": [
                {
                    "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, key),
                    "fallback": "Nope?",
                    "attachment_type": "default",
                }
            ]
        }
        print(message)

        requests.post(
            data['response_url'],
            headers={
                'Content-Type':'application/json;charset=UTF-8',
                'Authorization': 'Bearer %s' % slack_token
            },
            json=message
        )
        s3 = boto3.resource('s3')
        s3.Object(bucket_name, key).delete()


    if data['actions'][0]['name'] == 'username':
        user_id = data['actions'][0]['selected_options'][0]['value']
        new_key = 'trained/%s/%s.jpg' % (user_id, hashlib.md5(key.encode('utf-8')).hexdigest())

        message = {
            "text": "Trained as %s" % user_id,
            "attachments": [
                {
                    "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, new_key),
                    "fallback": "Nope?",
                    "attachment_type": "default",
                }
            ]
        }
        print(message)
        requests.post(data['response_url'], headers={'Content-Type':'application/json;charset=UTF-8', 'Authorization': 'Bearer %s' % slack_token}, json=message)

        # response is send, start training
        client = boto3.client('rekognition')
        resp = client.index_faces(
            CollectionId=rekognition_collection_id,
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': key,
                }
            },
            ExternalImageId=user_id,
            DetectionAttributes=['DEFAULT']
        )

        # move the s3 file to the 'trained' location
        s3 = boto3.resource('s3')
        s3.Object(bucket_name, new_key).copy_from(CopySource='%s/%s' % (bucket_name, key))
        s3.ObjectAcl(bucket_name, new_key).put(ACL='public-read')
        s3.Object(bucket_name, key).delete()

    return {
        "statusCode": 200
    }
