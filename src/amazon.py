#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3

model='arn:aws:rekognition:eu-west-1:734486874644:project/garbage_rekog/version/garbage_rekog.2023-03-17T11.54.36/1679054076305'
min_confidence=50
client=boto3.client('rekognition')

def show_custom_labels(imageBytes):

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'Bytes': imageBytes},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    # display_image(bucket,photo,response)
    print(response)
    return response['CustomLabels']