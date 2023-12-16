
"""
Frontend module for the Flask application.

This module defines a simple Flask application that serves as the frontend for the project.
"""


from flask import Flask, render_template, request
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'


FASTAPI_BACKEND_HOST = 'http://backend'
BACKEND_URL = f'{FASTAPI_BACKEND_HOST}/query/'


class AddressesForm(FlaskForm):
    areas = []
    response = requests.get('http://backend/areas')
    if response.status_code == 200:
        areas = response.json()
    area_name = SelectField('Area name:', choices=[(area, area) for area in areas])
    submit = SubmitField('Get Area_name from FastAPI Backend')


class ProviderForm(FlaskForm):
    provider_name = SelectField()

    
class QueryForm(FlaskForm):
    street_name = StringField('Street name:')
    submit = SubmitField('Get number of columns from FastAPI Backend')


class ProviderstreetnameForm(FlaskForm):
    street_name = StringField('Street Name:')
    submit = SubmitField('Search')

    
class ZoneForm(FlaskForm):
    zone_name=StringField('Zone name')
    submit=SubmitField('Get types of sockets from FASTAPI Backend')
    

@app.route('/')
def index():
    """
    Render the index page.

    Returns:
        str: Rendered HTML content for the index page.
    """

    date_from_backend = fetch_date_from_backend()
    return render_template('index.html', date_from_backend=date_from_backend)
  

def fetch_date_from_backend():
    """
    Fetch the current date from the backend.

    Returns:
        str: The current date in ISO format, or a default message if not available.
    """


    backend_url = 'http://backend/get-date'
    try:
        response = requests.get(backend_url)
        response.raise_for_status()
        return response.json().get('date', 'Date not available')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching date from backend: {e}")
        return 'Area name not available'



@app.route('/addresses', methods=['GET', 'POST'])
def addresses():
    """
    Render the addresses page.

    Returns:
        str: Rendered HTML content for the addresses page in order to show street names present in a specific zone.
    """
    form = AddressesForm()
    error_message = None 

    if form.validate_on_submit():
        selected_area = form.area_name.data
        fastapi_url = f'{FASTAPI_BACKEND_HOST}/addresses/{selected_area}'
        response = requests.get(fastapi_url)
        if response.status_code == 200:
            return render_template('addresses.html', form=form, result=response.text, error_message=error_message)
        else:
            error_message = f'Error: Unable to fetch area_name for {selected_area} from FastAPI Backend'
    return render_template('addresses.html', form=form, result=None, error_message=error_message)



@app.route('/provider', methods=['GET', 'POST'])
def provider():
    """
    Render the provider page.

    Returns:
        str: Rendered HTML content for the provider page in order to know which street a specific provider is present.
    """
    error_message = None  
    form = None 

    if request.method == 'POST':
        provider_name = request.form.get('provider_name')
        fastapi_url = f'{FASTAPI_BACKEND_HOST}/module/lookfor/{provider_name}'
        response = requests.get(fastapi_url)
        
        if response.status_code == 200:
            data = response.json()
            form = ProviderForm()
            return render_template('provider.html', form=form, result=data, error_message=error_message)
        else:
            error_message = f'Error: Unable to fetch data for {provider_name} from FastAPI Backend'

    form = ProviderForm()
    return render_template('provider.html', form=form, result=None, error_message=error_message)


@app.route('/street_name', methods=['GET','POST'])
def provider_street_name():
    """
    Render the street name page.

    Returns:
        str: Rendered HTML content for the street name page in order to know which provider is present in the street written as input.
    """

    form = ProviderstreetnameForm()
    error_message= None

    if form.validate_on_submit():
        street_name = form.street_name.data
        fastapi_url = f'{FASTAPI_BACKEND_HOST}/module/search/{street_name}'
        response = requests.get(fastapi_url)
        if response.status_code == 200:
            data = response.json()
            return render_template('street_name1.html', form=form, result=data, error_message=error_message)
        else:
            error_message = f'Error: Unable to fetch data for {street_name} form FastAPI backend'
    return render_template('street_name1.html', form=form, result=None, error_message=error_message)


@app.route('/number_stations', methods=['GET', 'POST'])
def number_stations():
    """
    Render the number of stations page.

    Returns:
        str: Rendered HTML content for the number of stations page to know how many charging stations are present in a specific street.
    """

    form = QueryForm()
    error_message = None

    if form.validate_on_submit():
        street_name = form.street_name.data
        fastapi_url = f'{FASTAPI_BACKEND_HOST}/get_charging_stations/{street_name}'
        response = requests.get(fastapi_url)

        if response.status_code == 200:
            data = response.json()
            return render_template('number_stations.html', form=form, result=data, error_message=error_message)
        else:
            error_message = f'Error: Unable to fetch dict_vie for {street_name} from FastAPI Backend'

    return render_template('number_stations.html', form=form, result=None, error_message=error_message)

    
@app.route('/socket_types', methods=['GET', 'POST'])
def socket_types():
    """
    Render the socket types page.

    Returns:
        str: Rendered HTML content for the socket types page to discover which type of socket (AC Normal or AC-DC Fast) is present in the street written as input.
    """
    error_message = None
    form = None

    if request.method == 'POST':
        zone_name = request.form.get('zone_name')
        fastapi_url = f'{FASTAPI_BACKEND_HOST}/socket_types_by_zone/{zone_name}'
        response = requests.get(fastapi_url)

        if response.status_code == 200:
            data = response.json()
            form = ZoneForm()
            return render_template('socket_types.html', form=form, result=data, error_message=error_message)
        else:
            error_message = f'Error: Unable to fetch data for {zone_name} from FASTAPI backend'

    form = ZoneForm()
    return render_template('socket_types.html', form=form, result=None, error_message=error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

