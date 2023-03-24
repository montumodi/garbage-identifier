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

# # Define the emissions savings per unit of material recycled
# emissions_savings = {
#     'Paper/Cardboard': 0.71,
#     'Glass': 0.23,
#     'Plastic': 1.13,
#     'Battery': 2.34,
#     'Organic': 0.46,
#     'Clothes': 1.08,
#     'E-Waste': 1.18,
#     'Light Bulbs': 0.32,
#     'Metal': 1.34
# }

# # Define the weight of each material recycled
# material_weights = {
#     'Paper/Cardboard': 2000,
#     'Glass': 1000,
#     'Plastic': 500,
#     'Battery': 50,
#     'Organic': 100,
#     'Clothes': 150,
#     'E-Waste': 75,
#     'Light Bulbs': 25,
#     'Metal': 250
# }

# # Create a dictionary of material weights in kg
# average_material_weights = {
#     'Paper/Cardboard': 0.005, # 0.5 kg per 100 sheets of standard copy paper
#     'Glass': 0.8, # 0.8 kg per 1 liter bottle
#     'Plastic': 0.05, # 0.05 kg per plastic bottle or container
#     'Battery': 0.05, # 0.05 kg per AA battery
#     'Organic': 0.1, # 0.1 kg per day of food waste (varies depending on moisture content)
#     'Clothes': 0.5, # 0.5 kg per shirt or pair of pants
#     'E-Waste': 3, # 3 kg per desktop computer or laptop
#     'Light Bulbs': 0.1, # 0.1 kg per compact fluorescent bulb (CFL)
#     'Metal': 0.2 # 0.2 kg per aluminum can or food tin
# }

# # Calculate the carbon emissions saved for each material
# carbon_emissions = {k: v * emissions_savings[k] * material_weights[k] / 1000 for k, v in emissions_savings.items()}

# # Create a bar chart of the carbon emissions saved
# data = [go.Bar(x=list(carbon_emissions.keys()), y=list(carbon_emissions.values()))]
# layout = go.Layout(title='Carbon Emissions Saved by Recycling',
#                    xaxis={'title': 'Material'},
#                    yaxis={'title': 'Carbon Emissions Saved (kg CO2e)'})

app.layout = html.Div(className='container', children=[
    Row(html.H1("It's not a trash")),
    # Row(dcc.Graph(id='emissions-graph', figure={'data': data, 'layout': layout})),
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
        multiple=False
    )),
    Row(dcc.Graph(id='model-output', style={"height": "70vh"}))
])

def sortFunc(e):
    return e["probability"]

@app.callback(
    Output('model-output', 'figure'),
    [Input('upload-image', 'contents')])
def run_model(list_of_contents):
    if list_of_contents is not None:
        base64Image = base64.b64decode(list_of_contents.split(",")[1])
        img = Image.open(io.BytesIO(base64Image))
        tstart = time.time()
        predictions = predict_image(img)
        tend = time.time()
        fig = pil_to_fig(img, showlegend=True, title=f'Predictions took {tend-tstart:.2f}s')
        predictions = sorted(predictions["predictions"], key=sortFunc, reverse=True)
        predictions = list(filter(lambda item: item["probability"] >= 0.5, predictions))
        img_width, img_height = img.size
        for bbox in predictions:
            left = bbox["boundingBox"]["left"]
            width = bbox["boundingBox"]["width"]
            height = bbox["boundingBox"]["height"]
            top = bbox["boundingBox"]["top"]

            x0 = left * img_width
            y0 = top * img_height
            x1 = (left + width) * img_width
            y1 = (top + height) * img_height
            label = bbox["tagName"]
            confidence = bbox["probability"]
            tagId = bbox["tagId"]
            text = f"class={label}<br>confidence={confidence:.3f}"
            add_bbox(
                fig, x0, y0, x1, y1,
                opacity=0.7, group=label, name=label, color=COLORS[tagId],
                showlegend=True, text=text
            )

        return fig
    raise dash.exceptions.PreventUpdate


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
