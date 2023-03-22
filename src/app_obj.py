import base64
from io import BytesIO
import time
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from predict_object_detection import initialize, predict_image
from PIL import Image

initialize()

# plotly.py helper functions


def pil_to_b64(im, enc="png"):
    io_buf = BytesIO()
    im.save(io_buf, format=enc)
    encoded = base64.b64encode(io_buf.getvalue()).decode("utf-8")
    return f"data:img/{enc};base64, " + encoded

# Dash component wrappers


def Row(children=None, **kwargs):
    return html.Div(children, className="row", **kwargs)


def pil_to_fig(im, showlegend=False, title=None):
    img_width, img_height = im.size
    fig = go.Figure()
    # This trace is added to help the autoresize logic work.
    fig.add_trace(go.Scatter(
        x=[img_width * 0.05, img_width * 0.95],
        y=[img_height * 0.95, img_height * 0.05],
        showlegend=False, mode="markers", marker_opacity=0,
        hoverinfo="none", legendgroup='Image'))

    fig.add_layout_image(dict(
        source=pil_to_b64(im), sizing="stretch", opacity=1, layer="below",
        x=0, y=0, xref="x", yref="y", sizex=img_width, sizey=img_height,))

    # Adapt axes to the right width and height, lock aspect ratio
    fig.update_xaxes(
        showgrid=False, visible=False, constrain="domain", range=[0, img_width])

    fig.update_yaxes(
        showgrid=False, visible=False,
        scaleanchor="x", scaleratio=1,
        range=[img_height, 0])

    fig.update_layout(title=title, showlegend=showlegend)

    return fig


def add_bbox(fig, x0, y0, x1, y1,
             showlegend=True, name=None, color=None,
             opacity=0.5, group=None, text=None):
    fig.add_trace(go.Scatter(
        x=[x0, x1, x1, x0, x0],
        y=[y0, y0, y1, y1, y0],
        mode="lines",
        fill="toself",
        opacity=opacity,
        marker_color=color,
        hoveron="fills",
        name=name,
        hoverlabel_namelength=0,
        text=text,
        legendgroup=group,
        showlegend=showlegend,
    ))


# colors for visualization
COLORS = ['#fe938c', '#86e7b8', '#f9ebe0', '#208aae', '#fe4a49',
          '#291711', '#5f4b66', '#b98b82', '#87f5fb', '#63326e'] * 50


# Start Dash
app = dash.Dash(__name__)
server = app.server  # Expose the server variable for deployments

app.layout = html.Div(className='container', children=[
    Row(html.H1("Dash Object Detection App")),
    Row(dcc.Upload(
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
    )),
    Row(dcc.Graph(id='model-output', style={"height": "70vh"}))
])


def myFunc(e):
    return e["probability"]


@app.callback(
    Output('model-output', 'figure'),
    [Input('upload-image', 'contents')])
def run_model(list_of_contents):
    if list_of_contents is not None:
        im = base64.b64decode(list_of_contents[0].split(",")[1])
        img = Image.open(io.BytesIO(im))
        fig = pil_to_fig(img, showlegend=True, title='Predictions')
        myList = predict_image(img)
        myList = sorted(myList["predictions"], key=myFunc, reverse=True)
        myList = list(filter(lambda item: item["probability"] >= 0.5, myList))
        img_height, img_width = img.size
        for bbox in myList:
            x0 = bbox["boundingBox"]["left"] * img_width
            y0 = bbox["boundingBox"]["top"] * img_width
            x1 = (bbox["boundingBox"]["left"] +
                  bbox["boundingBox"]["width"]) * img_height
            y1 = (bbox["boundingBox"]["top"] +
                  bbox["boundingBox"]["height"]) * img_height
            text = bbox["tagName"]
            label = bbox["tagName"]

            add_bbox(
                fig, x0, y0, x1, y1,
                opacity=0.7, group=label, name=label, color=COLORS[bbox["tagId"]],
                showlegend=True, text=text
            )

        return fig
    raise dash.exceptions.PreventUpdate


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
