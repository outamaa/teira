#!/usr/bin/python
import boto
from boto.s3.key import Key
from boto.s3.connection import OrdinaryCallingFormat
import os
import picamera
import sys
import time

# http://stackabuse.com/example-upload-a-file-to-aws-s3/
def upload_to_s3(aws_access_key_id, aws_secret_access_key, file, bucket, key, callback=None, md5=None, reduced_redundancy=False, content_type=None):
    """
    Uploads the given file to the AWS S3
    bucket and key specified.

    callback is a function of the form:

    def callback(complete, total)

    The callback should accept two integer parameters,
    the first representing the number of bytes that
    have been successfully transmitted to S3 and the
    second representing the size of the to be transmitted
    object.

    Returns boolean indicating success/failure of upload.
    """
    try:
        size = os.fstat(file.fileno()).st_size
    except:
        # Not all file objects implement fileno(),
        # so we fall back on this
        file.seek(0, os.SEEK_END)
        size = file.tell()

    conn = boto.s3.connect_to_region('eu-central-1',
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     calling_format=OrdinaryCallingFormat(),
                                     host='s3.eu-central-1.amazonaws.com')
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)
    k.key = key
    if content_type:
        k.set_metadata('Content-Type', content_type)
    sent = k.set_contents_from_file(file, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy, rewind=True)

    # Rewind for later use
    file.seek(0)

    if sent == size:
        return True
    return False

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", None)
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", None)

UPLOAD_FILENAME = sys.argv[1]
BUCKET_NAME = sys.argv[2]

with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    time.sleep(10)
    camera.capture(UPLOAD_FILENAME, format='jpeg')
    f = open(UPLOAD_FILENAME, 'rb')
    if upload_to_s3(S3_ACCESS_KEY, S3_SECRET_KEY, f, BUCKET_NAME, UPLOAD_FILENAME):
        print 'Yay!'
    else:
        print 'Nej!'
