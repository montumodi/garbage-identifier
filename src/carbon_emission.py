import dash
import plotly.graph_objects as go
import dash_core_components as dcc

# Define the emissions savings per unit of material recycled
emissions_savings = {
    'Paper': 0.71,
    'Cardboard': 0.71,
    'Glass': 0.23,
    'Plastic': 1.13,
    'Batteries': 2.34,
    'Organic': 0.46,
    'Clothes': 1.08,
    'e-Waste': 1.18,
    'Light Bulb': 0.32,
    'Metal': 1.34
}

# Create a dictionary of material weights in kg
average_material_weights = {
    'Paper': 0.005, # 0.5 kg per 100 sheets of standard copy paper,
    'Cardboard': 0.005,
    'Glass': 0.8, # 0.8 kg per 1 liter bottle
    'Plastic': 0.05, # 0.05 kg per plastic bottle or container
    'Batteries': 0.05, # 0.05 kg per AA battery
    'Organic': 0.1, # 0.1 kg per day of food waste (varies depending on moisture content)
    'Clothes': 0.5, # 0.5 kg per shirt or pair of pants
    'e-Waste': 3, # 3 kg per desktop computer or laptop
    'Light Bulb': 0.1, # 0.1 kg per compact fluorescent bulb (CFL)
    'Metal': 0.2 # 0.2 kg per aluminum can or food tin
}

def get_carbon_emission_graph(predictions):
    # Define the weight of each material recycled
    material_weights = {
        'Paper': 0,
        'Cardboard': 0,
        'Glass': 0,
        'Plastic': 0,
        'Batteries': 0,
        'Organic': 0,
        'Clothes': 0,
        'e-Waste': 0,
        'Light Bulb': 0,
        'Metal': 0
    }

    for prediction in predictions:
        label = prediction["tagName"]
        material_weights[label] = material_weights[label] + average_material_weights[label]

    # Calculate the carbon emissions saved for each material
    carbon_emissions = {k: v * emissions_savings[k] * material_weights[k] / 1000 for k, v in emissions_savings.items()}

    # Create a bar chart of the carbon emissions saved
    data = [go.Bar(x=list(carbon_emissions.keys()), y=list(carbon_emissions.values()))]
    layout = go.Layout(title='Carbon Emissions Saved by Recycling',
                    xaxis={'title': 'Material'},
                    yaxis={'title': 'Carbon Emissions Saved (kg CO2e)'})
    
    return dcc.Graph(figure={'data': data, 'layout': layout})