from urllib.request import urlopen
from datetime import datetime
import tensorflow as tf

from PIL import Image
import numpy as np

import mscviplib

filename = '../model/recycle_type_classification/model.pb'
labels_filename = '../model/recycle_type_classification/labels.txt'

network_input_size = 0

output_layer = 'model_output:0'
input_node = 'data:0'

graph = tf.Graph()
graph_def = tf.compat.v1.GraphDef()
labels = []


def initialize():
    print('Loading model...', end=''),
    with graph.as_default():
        with open(filename, 'rb') as f:
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')

    # Retrieving 'network_input_size' from shape of 'input_node'
    with tf.compat.v1.Session(graph=graph) as sess:
        input_tensor_shape = sess.graph.get_tensor_by_name(input_node).shape.as_list()

    assert len(input_tensor_shape) == 4
    assert input_tensor_shape[1] == input_tensor_shape[2]

    global network_input_size
    network_input_size = input_tensor_shape[1]

    print('Success!')
    print('Loading labels...', end='')
    with open(labels_filename, 'rt') as lf:
        global labels
        labels = [label.strip() for label in lf.readlines()]
    print(len(labels), 'found. Success!')


def log_msg(msg):
    print("{}: {}".format(datetime.now(), msg))


def predict_url(imageUrl):
    """
    predicts image by url
    """
    log_msg("Predicting from url: " + imageUrl)
    with urlopen(imageUrl) as testImage:
        image = Image.open(testImage)
        return predict_image(image)


def update_orientation(image):
    """
    corrects image orientation according to EXIF data
    image: input PIL image
    returns corrected PIL image
    """
    exif_orientation_tag = 0x0112
    if hasattr(image, '_getexif'):
        exif = image._getexif()
        if exif is not None and exif_orientation_tag in exif:
            orientation = exif.get(exif_orientation_tag, 1)
            log_msg('Image has EXIF Orientation: ' + str(orientation))
            # orientation is 1 based, shift to zero based and flip/transpose based on 0-based values
            orientation -= 1
            if orientation >= 4:
                image = image.transpose(Image.TRANSPOSE)
            if orientation == 2 or orientation == 3 or orientation == 6 or orientation == 7:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            if orientation == 1 or orientation == 2 or orientation == 5 or orientation == 6:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
    return image


def predict_image(image):
    """
    calls model's image prediction
    image: input PIL image
    returns prediction response as a dictionary. To get predictions, use result['predictions'][i]['tagName'] and result['predictions'][i]['probability']
    """
    log_msg('Predicting image')
    try:
        print(image.mode)
        if image.mode != "RGB":
            log_msg("Converting to RGB")
            image = image.convert("RGB")

        w, h = image.size
        log_msg("Image size: " + str(w) + "x" + str(h))

        # Update orientation based on EXIF tags
        image = update_orientation(image)

        metadata = mscviplib.GetImageMetadata(image)
        cropped_image = mscviplib.PreprocessForInferenceAsTensor(metadata,
                                                                 image.tobytes(),
                                                                 mscviplib.ResizeAndCropMethod.CropCenter,
                                                                 (network_input_size, network_input_size),
                                                                 mscviplib.InterpolationType.Bilinear,
                                                                 mscviplib.ColorSpace.RGB, (), ())
        cropped_image = np.moveaxis(cropped_image, 0, -1)

        with tf.compat.v1.Session(graph=graph) as sess:
            prob_tensor = sess.graph.get_tensor_by_name(output_layer)
            predictions, = sess.run(prob_tensor, {input_node: [cropped_image]})

            result = []
            for p, label in zip(predictions, labels):
                truncated_probablity = np.float64(round(p, 8))
                if truncated_probablity > 1e-8:
                    result.append({
                        'tagName': label,
                        'probability': truncated_probablity,
                        'tagId': '',
                        'boundingBox': None})

            response = {
                'id': '',
                'project': '',
                'iteration': '',
                'created': datetime.utcnow().isoformat(),
                'predictions': result
            }

            # log_msg("Results: " + str(response))
            return response

    except Exception as e:
        log_msg(str(e))
        return 'Error: Could not preprocess image for prediction. ' + str(e)
