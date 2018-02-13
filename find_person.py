import os
from threading import Timer
import time
import datetime
import awscam
import cv2
from botocore.session import Session
from threading import Thread

# Setup the S3 client
session = Session()
s3 = session.create_client('s3')
s3_bucket = 'doorman-faces'

# setup the camera and frame
ret, frame = awscam.getLastFrame()
ret,jpeg = cv2.imencode('.jpg', frame)
Write_To_FIFO = True
class FIFO_Thread(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)

    def run(self):
        # write to tmp file for local debugging purpose
        fifo_path = "/tmp/results.mjpeg"
        if not os.path.exists(fifo_path):
            os.mkfifo(fifo_path)
        f = open(fifo_path,'w')

        # yay, succesful, let's start streaming to the file
        while Write_To_FIFO:
            try:
                f.write(jpeg.tobytes())
            except IOError as e:
                continue

def greengrass_infinite_infer_run():
    try:
        modelPath = "/opt/awscam/artifacts/mxnet_deploy_ssd_resnet50_300_FP16_FUSED.xml"
        modelType = "ssd"
        input_width = 300
        input_height = 300
        max_threshold = 0.60  # raise/lower this value based on your conditions
        outMap = { 1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat', 5: 'bottle', 6: 'bus', 7 : 'car', 8 : 'cat', 9 : 'chair', 10 : 'cow', 11 : 'dinning table', 12 : 'dog', 13 : 'horse', 14 : 'motorbike', 15 : 'person', 16 : 'pottedplant', 17 : 'sheep', 18 : 'sofa', 19 : 'train', 20 : 'tvmonitor' }
        results_thread = FIFO_Thread()
        results_thread.start()

        # Load model to GPU
        mcfg = {"GPU": 1}
        model = awscam.Model(modelPath, mcfg)

        # try to get a frame from the camera
        ret, frame = awscam.getLastFrame()
        if ret == False:
            raise Exception("Failed to get frame from the stream")

        yscale = float(frame.shape[0]/input_height)
        xscale = float(frame.shape[1]/input_width)

        doInfer = True
        while doInfer:
            # Get a frame from the video stream
            ret, frame = awscam.getLastFrame()

            # Raise an exception if failing to get a frame
            if ret == False:
                raise Exception("Failed to get frame from the stream")

            # Resize frame to fit model input requirement
            frameResize = cv2.resize(frame, (input_width, input_height))

            # Run model inference on the resized frame
            inferOutput = model.doInference(frameResize)

            # Output inference result to the fifo file so it can be viewed with mplayer
            parsed_results = model.parseResult(modelType, inferOutput)['ssd']
            label = '{'
            for obj in parsed_results:
                if obj['prob'] > max_threshold:
                    xmin = int( xscale * obj['xmin'] ) + int((obj['xmin'] - input_width/2) + input_width/2)
                    ymin = int( yscale * obj['ymin'] )
                    xmax = int( xscale * obj['xmax'] ) + int((obj['xmax'] - input_width/2) + input_width/2)
                    ymax = int( yscale * obj['ymax'] )

                    # if a person was found, upload the target area to S3 for further inspection
                    if outMap[obj['label']] == 'person':

                        # get the person image
                        person = frame[ymin:ymax, xmin:xmax]

                        # create a nice s3 file key
                        s3_key = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H_%M_%S.%f') + '.jpg'
                        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 90]  # 90% should be more than enough
                        _, jpg_data = cv2.imencode('.jpg', person, encode_param)
                        filename = "incoming/%s" % s3_key  # the guess lambda function is listening here
                        response = s3.put_object(ACL='public-read', Body=jpg_data.tostring(),Bucket=s3_bucket,Key=filename)

                    # draw a rectangle around the designated area, and tell what label was found
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 165, 20), 4)
                    label += '"{}": {:.2f},'.format(outMap[obj['label']], obj['prob'] )
                    label_show = "{}:    {:.2f}%".format(outMap[obj['label']], obj['prob']*100 )
                    cv2.putText(frame, label_show, (xmin, ymin-15),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 20), 4)
            label += '"null": 0.0'
            label += '}'

            global jpeg
            ret,jpeg = cv2.imencode('.jpg', frame)

    except Exception as e:
        print "Crap, something failed: %s" % str(e)

    # Asynchronously schedule this function to be run again in 15 seconds
    Timer(15, greengrass_infinite_infer_run).start()

# Execute the function above
greengrass_infinite_infer_run()


# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    return
