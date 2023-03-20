import cv2
from predict import predict_image
import tensorflow as tf
import numpy as np
import dash_html_components as html
from dash import dash_table


# Set the size of the image (in pixels)
img_width = 640
img_height = 480
def myFunc(e):
  return e["probability"]
def open_camera():
    print("\n", "*"*8, "Starting camera!", "*"*8, "\n")
    # Take an image from the camera and save it
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, img_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, img_height)

    # ret, image = camera.read()
    # cv2.imwrite('capture.png', image)
    ret, image_np = camera.read()

    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    # image_np_expanded = np.expand_dims(image_np, axis=0)

    # Things to try:
    # Flip horizontally
    # image_np = np.fliplr(image_np).copy()

    # Convert image to grayscale
    # image_np = np.tile(
    #     np.mean(image_np, 2, keepdims=True), (1, 1, 3)).astype(np.uint8)

    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)

    results = predict_image(input_tensor)
    print("\n", "*"*8, "Captured image saved!", "*"*8, "\n")
    print("\n", "*"*8, "Results", "*"*8, results, "\n")
    # myList = sorted(results["predictions"], key=myFunc, reverse=True)
    html.Div([
        # html.Div(myList[0]["tagName"]),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Hr(),
        # dash_table.DataTable(myList)
    ])

    # Select color for the bounding box (BGR)
    # colors = {
    #     "tomato": (0,215,255),
    #     "cucumber": (255,215,0),
    #     "pepper": (66,174,255)
    # }

    # Display the results
    # for prediction in results:
    #     if prediction['probability'] > 0.3:
    #         print(f"{prediction['tagName']}: {prediction['probability'] * 100 :.2f}%")
    #         color = colors[prediction['tagName']]
    #         left = prediction['boundingBox']['left'] * img_width
    #         top = prediction['boundingBox']['top'] * img_height
    #         height = prediction['boundingBox']['height'] * img_height
    #         width =  prediction['boundingBox']['width'] * img_width
    #         result_image = cv2.rectangle(image, (int(left), int(top)), (int(left + width), int(top + height)), color, 3)
    #         cv2.putText(result_image, f"{prediction['tagName']}: {prediction['probability'] * 100 :.2f}%", (int(left), int(top)-10), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 0.5, color = color, thickness = 2)
    #         cv2.imwrite('result.png', result_image)

    camera.release()

def opencamera():
    video_capture = cv2.VideoCapture(0)

    cv2.namedWindow("Window")

    while True:
        ret, frame = video_capture.read()
        cv2.imshow("Window", frame)

        #This breaks on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()