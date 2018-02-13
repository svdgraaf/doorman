Doorman
-------
This will greet your coworkers on slack when they enter the office.

This was send in as part of the [AWS Deeplens Hackaton](https://devpost.com/software/doorman-a1oh0e)


Setup
-----
Quite a few steps, needs cleanup, most of it can be automated.

- Create a bucket, remember the name, make sure that your deeplens user can write to this bucket.
- Create a Rekognition collection (and note the collecition id)
- Be sure to have the following env vars in your environment:
  - BUCKET_NAME=your-bucket-name
  - SLACK_API_TOKEN=your-slack-token
  - SLACK_CHANNEL_ID="slack-channel-id"
  - REKOGNITION_COLLECTION_ID="your-collection-id"

- Deploy the lambda functions with Serverles (eg: `sls deploy`), this will create a CF stack with your functions. Note the api gateway endpoint, you'll need it later

- Go into the deeplens console, and create a project, select the "Object detection" model
- Remove the `deeplens-object-detection` function, and add a function for `find_person`
- Deploy the application to your deeplens

- Go to the [slack api](https://api.slack.com/apps), and click "create a new app".
- Give a name, and select your workspace
- Activate:
  - Incoming webhooks
  - Interactive components (use the api gateway endpoint that you noted before, ignore `Load URL`)
  - Permissions: Install the app in your workspace, and note the token. You'll need `chat:write:bot`, `channels:read` and `incoming-webhook`.
- Deploy the app again with the new environment variables

That should be it. Whenever the Deeplens rekognizes someone, it will upload into the S3 bucket. Which will trigger the other lambda functions.

Architecture
------------
![Architecture](https://challengepost-s3-challengepost.netdna-ssl.com/photos/production/software_photos/000/602/534/datas/gallery.jpg)

Video
-----
[![Video](https://img.youtube.com/vi/UXVD22jDbu8/0.jpg)](https://www.youtube.com/watch?v=UXVD22jDbu8)
