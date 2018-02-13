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

from doorman import guess
from doorman import train
from doorman import unknown
#
#
# if __name__ == "__main__":
#     print(unknown(
#         {
#           "Records": [
#             {
#               "eventVersion": "2.0",
#               "eventTime": "1970-01-01T00:00:00.000Z",
#               "requestParameters": {
#                 "sourceIPAddress": "127.0.0.1"
#               },
#               "s3": {
#                 "configurationId": "testConfigRule",
#                 "object": {
#                   "eTag": "0123456789abcdef0123456789abcdef",
#                   "sequencer": "0A1B2C3D4E5F678901",
#                   "key": "detected/U033PFSFB/1ef4dfe223eec2b6801aa4873cd3e350.jpg",
#                   "size": 1024
#                 },
#                 "bucket": {
#                   "arn": "arn:aws:s3:::doorman-faces",
#                   "name": "doorman-faces",
#                   "ownerIdentity": {
#                     "principalId": "EXAMPLE"
#                   }
#                 },
#                 "s3SchemaVersion": "1.0"
#               },
#               "responseElements": {
#                 "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
#                 "x-amz-request-id": "EXAMPLE123456789"
#               },
#               "awsRegion": "us-east-1",
#               "eventName": "ObjectCreated:Put",
#               "userIdentity": {
#                 "principalId": "EXAMPLE"
#               },
#               "eventSource": "aws:s3"
#             }
#           ]
#         }, {})
#     )
#
#     # print(train({
#     #     "resource": "/",
#     #     "path": "/",
#     #     "httpMethod": "POST",
#     #     "headers": {
#     #         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#     #         "Accept-Encoding": "gzip, deflate, br",
#     #         "Accept-Language": "en-GB,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4",
#     #         "cache-control": "max-age=0",
#     #         "CloudFront-Forwarded-Proto": "https",
#     #         "CloudFront-Is-Desktop-Viewer": "true",
#     #         "CloudFront-Is-Mobile-Viewer": "false",
#     #         "CloudFront-Is-SmartTV-Viewer": "false",
#     #         "CloudFront-Is-Tablet-Viewer": "false",
#     #         "CloudFront-Viewer-Country": "GB",
#     #         "content-type": "application/x-www-form-urlencoded",
#     #         "Host": "j3ap25j034.execute-api.eu-west-2.amazonaws.com",
#     #         "origin": "https://j3ap25j034.execute-api.eu-west-2.amazonaws.com",
#     #         "Referer": "https://j3ap25j034.execute-api.eu-west-2.amazonaws.com/dev/",
#     #         "upgrade-insecure-requests": "1",
#     #         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
#     #         "Via": "2.0 a3650115c5e21e2b5d133ce84464bea3.cloudfront.net (CloudFront)",
#     #         "X-Amz-Cf-Id": "0nDeiXnReyHYCkv8cc150MWCFCLFPbJoTs1mexDuKe2WJwK5ANgv2A==",
#     #         "X-Amzn-Trace-Id": "Root=1-597079de-75fec8453f6fd4812414a4cd",
#     #         "X-Forwarded-For": "50.129.117.14, 50.112.234.94",
#     #         "X-Forwarded-Port": "443",
#     #         "X-Forwarded-Proto": "https"
#     #     },
#     #     "queryStringParameters": "",
#     #     "pathParameters": "None",
#     #     "stageVariables": "None",
#     #     "requestContext": {
#     #         "path": "/dev/",
#     #         "accountId": "125002137610",
#     #         "resourceId": "qdolsr1yhk",
#     #         "stage": "dev",
#     #         "requestId": "0f2431a2-6d2f-11e7-b75152aa497861",
#     #         "identity": {
#     #             "cognitoIdentityPoolId": None,
#     #             "accountId": None,
#     #             "cognitoIdentityId": None,
#     #             "caller": None,
#     #             "apiKey": "",
#     #             "sourceIp": "50.129.117.14",
#     #             "accessKey": None,
#     #             "cognitoAuthenticationType": None,
#     #             "cognitoAuthenticationProvider": None,
#     #             "userArn": None,
#     #             "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
#     #             "user": None
#     #         },
#     #         "resourcePath": "/",
#     #         "httpMethod": "POST",
#     #         "apiId": "j3azlsj0c4"
#     #     },
#     #     "body": "payload=%7B%22type%22%3A%22interactive_message%22%2C%22actions%22%3A%5B%7B%22name%22%3A%22discard%22%2C%22type%22%3A%22select%22%2C%22selected_options%22%3A%5B%7B%22value%22%3A%22U033PFSFB%22%7D%5D%7D%5D%2C%22callback_id%22%3A%22unknown%5C%2Ftest.jpg%22%2C%22team%22%3A%7B%22id%22%3A%22T02HUP4V7%22%2C%22domain%22%3A%22unitt%22%7D%2C%22channel%22%3A%7B%22id%22%3A%22C8HLA7R63%22%2C%22name%22%3A%22whodis%22%7D%2C%22user%22%3A%7B%22id%22%3A%22U033PFSFB%22%2C%22name%22%3A%22svdgraaf%22%7D%2C%22action_ts%22%3A%221513682920.702541%22%2C%22message_ts%22%3A%221513654753.000074%22%2C%22attachment_id%22%3A%221%22%2C%22token%22%3A%22QfG0e3Guj5VqB8FYRu6t6hsG%22%2C%22is_app_unfurl%22%3Afalse%2C%22original_message%22%3A%7B%22text%22%3A%22Whodis%3F%22%2C%22username%22%3A%22Doorman%22%2C%22bot_id%22%3A%22B8GHY4N9G%22%2C%22attachments%22%3A%5B%7B%22fallback%22%3A%22Nope%3F%22%2C%22image_url%22%3A%22https%3A%5C%2F%5C%2Fs3.amazonaws.com%5C%2Fdoorman-faces%5C%2Funknown%5C%2Ftest.jpg%22%2C%22image_width%22%3A720%2C%22image_height%22%3A480%2C%22image_bytes%22%3A85516%2C%22callback_id%22%3A%22unknown%5C%2Ftest.jpg%22%2C%22id%22%3A1%2C%22color%22%3A%223AA3E3%22%2C%22actions%22%3A%5B%7B%22id%22%3A%221%22%2C%22name%22%3A%22username%22%2C%22text%22%3A%22Select+a+username...%22%2C%22type%22%3A%22select%22%2C%22data_source%22%3A%22users%22%7D%5D%7D%5D%2C%22type%22%3A%22message%22%2C%22subtype%22%3A%22bot_message%22%2C%22ts%22%3A%221513654753.000074%22%7D%2C%22response_url%22%3A%22https%3A%5C%2F%5C%2Fhooks.slack.com%5C%2Factions%5C%2FT02HUP4V7%5C%2F288116281232%5C%2FqaNuNww7z6pywPrk3jIHHcHF%22%2C%22trigger_id%22%3A%22288701768947.2606786993.b007d1a39a5076df879809512ef1d063%22%7D",
#     #     "isBase64Encoded": False
#     #     }, {}))
#
#     # print(guess({'Records': [{'eventVersion': '2.0', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2017-12-19T12:04:09.653Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROAIHE5RTNGNONLAZCZS:AssumeRoleSession'}, 'requestParameters': {'sourceIPAddress': '63.228.166.237'}, 'responseElements': {'x-amz-request-id': '839246E5C0E2300C', 'x-amz-id-2': 'nZdfLBl9JptArE5YNYgD5vJhHjXSXZHPD8jFKSneIIJ8HWM4wiFvETRixxOVSJGenFGpqCFjckw='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'ca169f58-28da-4b01-a2c2-cdbbad9081c7', 'bucket': {'name': 'doorman-faces', 'ownerIdentity': {'principalId': 'AUAL9TOIHMDDI'}, 'arn': 'arn:aws:s3:::doorman-faces'}, 'object': {'key': 'detected/U033PFSFB/ac8b9fe608d6ec59871f5d2e2bcb8edd.jpg', 'size': 81715, 'eTag': '112ba09a09910f3d45508e31398b0517', 'sequencer': '005A39003941D63E04'}}}]}
#     # ,{}))
