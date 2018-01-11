import json
import boto3
import requests
import hashlib
import os

bucket_name = os.environ['BUCKET_NAME']
slack_token = os.environ['SLACK_API_TOKEN']
slack_channel_id = os.environ['SLACK_CHANNEL_ID']
rekognition_collection_id = os.environ['REKOGNITION_COLLECTION_ID']


def guess(event, context):
    client = boto3.client('rekognition')
    key = event['Records'][0]['s3']['object']['key']
    event_bucket_name = event['Records'][0]['s3']['bucket']['name']
    image = {
        'S3Object': {
            'Bucket': event_bucket_name,
            'Name': key
        }
    }
    # print(image)

    resp = client.search_faces_by_image(
        CollectionId=rekognition_collection_id,
        Image=image,
        MaxFaces=1,
        FaceMatchThreshold=70)

    s3 = boto3.resource('s3')

    if len(resp['FaceMatches']) == 0:
        # no known faces detected, let the users decide in slack
        print("No matches found, sending to unknown")
        new_key = 'unknown/%s.jpg' % hashlib.md5(key.encode('utf-8')).hexdigest()
        s3.Object(bucket_name, new_key).copy_from(CopySource='%s/%s' % (bucket_name, key))
        s3.ObjectAcl(bucket_name, new_key).put(ACL='public-read')
        s3.Object(bucket_name, key).delete()
    else:
        print ("Face found")
        print (resp)
        # move image
        user_id = resp['FaceMatches'][0]['Face']['ExternalImageId']
        new_key = 'detected/%s/%s.jpg' % (user_id, hashlib.md5(key.encode('utf-8')).hexdigest())
        s3.Object(bucket_name, new_key).copy_from(CopySource='%s/%s' % (event_bucket_name, key))
        s3.ObjectAcl(bucket_name, new_key).put(ACL='public-read')
        s3.Object(bucket_name, key).delete()

        # fetch the username for this user_id
        data = {
            "token": slack_token,
            "user": user_id
        }
        print(data)
        resp = requests.post("https://slack.com/api/users.info", data=data)
        print(resp.content)
        print(resp.json())
        username = resp.json()['user']['name']

        data = {
            "channel": slack_channel_id,
            "text": "Welcome @%s" % username,
            "link_names": True,
            "attachments": [
                {
                    "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, new_key),
                    "fallback": "Nope?",
                    "attachment_type": "default",
                }
            ]
        }
        resp = requests.post("https://slack.com/api/chat.postMessage", headers={'Content-Type':'application/json;charset=UTF-8', 'Authorization': 'Bearer %s' % slack_token}, json=data)
        return {}
