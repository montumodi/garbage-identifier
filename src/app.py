import datetime
import io
import json

import dash
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import base64

from PIL import Image
from predict import initialize, predict_image
from amazon import show_custom_labels
from camera import open_camera, opencamera

initialize()

app = dash.Dash(__name__)
# Expose Flask instance
server = app.server

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Button('Open Camera', id='open_camera', n_clicks=0),
    html.Div(id='output-image-upload'),
    html.Div(id='output-image-upload-camera', children='Enter a value and press submit')
])

def myFunc(e):
  return e["probability"]

def parse_contents(contents, filename, date, y):
    myList = sorted(y["predictions"], key=myFunc, reverse=True)
    return html.Div([
        html.Div(myList[0]["tagName"]),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents,height=500,width=500),
        html.Hr(),
        dash_table.DataTable(myList)
    ])

@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        base64Image = base64.b64decode(list_of_contents[0].split(",")[1]);
        img = Image.open(io.BytesIO(base64Image))
        Y = predict_image(img)
        #X = show_custom_labels(base64Image)
        #print(X)
        children = parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0], Y)
        return children


@app.callback(Output('output-image-upload-camera', 'children'),
              Input('open_camera', 'n_clicks'))
def start_camera(n_clicks):
    print("\n", "*"*8, "Camera opening", "*"*8, "\n")
    opencamera()
    #X = show_custom_labels(base64Image)
    #print(X)
    return html.Div(children='Incorrect Password',style={'padding-left':'550px','padding-top':'40px','font-size':'16px'})


if __name__ == '__main__':
    app.run_server(debug=True,port=8080)
