"""
Backend module for the FastAPI application.

This module defines a FastAPI application that serves
as the backend for the project.
"""

from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import pandas as pd
import csv
from typing import List

app = FastAPI()

df = pd.read_csv('/app/app/ricarica_colonnine.csv', sep=';')

@app.get('/areas', response_model=List[str])
def get_areas():
    areas = df['nome_nil'].unique().tolist()
    return areas


@app.get('/addresses/{name}', response_model=List[str])
def get_via_by_area(name: str):
    """
    Endpoint to get a list of street names based on the provided area name.

    Args:
        name (str): The name of the area.

    Returns:
        List[str]: A list of street names in the specified area.
    """
    name_lower = name.lower()
    filtered_data = df[df['nome_nil'].str.lower() == name_lower]
    if not filtered_data.empty:
        via_list = filtered_data['nome_via'].tolist()
        return via_list
    else:
        return []


@app.get('/')
def read_root():
    """
    Root endpoint for the backend.

    Returns:
        dict: A simple greeting.
    """
    return {"Hello": "World"}


@app.get('/module/search/{street_name}')
def get_charging_stations_provider_given_street_name(street_name):
    """
    Endpoint to get the charging station provider for a given street name.

    Args:
        street_name (str): The name of the street.

    Returns:
        str: A message indicating the provider for the charging station on the specified street. 
            If the street is not present in the database, a corresponding message is returned.
    """
    street_name=street_name.upper()
    charging_station=df[df['nome_via']== street_name]
    if not charging_station.empty:
        return f"The provider for the charging station present in {street_name} is {charging_station['titolare'].values[0]}"
    else:
        return f"Unfortunately the street name {street_name} is not present in our database"


@app.get('/module/lookfor/{provider_name}')
def get_charging_points_by_provider(provider_name):
    """
    Endpoint to get charging points based on the provided provider's name.

    Args:
        provider_name (str): The name of the charging point provider.

    Returns:
        List[dict]: List of dictionaries containing charging point information.
    """
    charging_points = []
    with open('/app/app/ricarica_colonnine.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        
        for row in reader:
            if row['titolare'].upper() == provider_name.upper():
                charging_points.append({
                    'localita': row['localita'].capitalize(),
                    'tipologia': row['tipologia'],
                    'numero_pdr': row['numero_pdr']
                })
    return charging_points


@app.get('/get_charging_point')
def numbers_of_stations_per_via(street_name):
    """
    Endpoint to get the number of charging stations based on the provided street name.

    Args:
        street_name (str): The name of the street.

    Returns:
        str: A message indicating the number of charging stations in the specified street.
            If the street is not present in the dataset, a corresponding message is returned.
    """

    selected_street = df[df['nome_via'] == street_name]
    
    if not selected_street.empty:
        number_of_stations = selected_street['numero_col'].sum()
        info_vie = number_of_stations
        return f"The number of charging stations in '{street_name}' is {info_vie}"
    else:
        return f"Unfortunately, the street '{street_name}' is not present in the dataset."


@app.get('/get_charging_stations/{street_name}')
def numbers_of_stations_per_via(street_name: str):
    """
    Endpoint to get the number of charging columns based on the street name.

    Args:
        street_name (str): The name of the street.

    Returns:
        dict: Information about the number of charging columns for the provided street name.
    """
    street_name = street_name.upper()  
    selected_street = df[df['nome_via'] == street_name]
    
    if not selected_street.empty:
        number_of_stations = selected_street['numero_col'].sum()  
        return f'The number of charging stations in {street_name} is {str(number_of_stations)}'
    else:
        return f"Unfortunately, the street '{street_name}' is not present in the dataset."


def numbers_of_stations_per_via(street_name_input: str = None):
    """
    Retrieve the number of charging stations based on the provided street name.

    Args:
        street_name_input (str, optional): The name of the street. Defaults to None.

    Returns:
        Union[str, dict]: If street_name_input is provided, returns information about
                          the number of charging stations for the provided street name.
                          If street_name_input is None, returns a default message.
    """

    if street_name_input is not None:
        result = numbers_of_stations_per_via(street_name_input)
        return result
    else:
        return '/'


def get_socket_types_by_zone(zone: str):
    """
    Retrieve the types of charging sockets based on the provided zone.

    Args:
        zone (str): The name of the zone.

    Returns:
        str: A message indicating the types of charging sockets in the specified zone.
            If the zone is not found, an HTTPException with status code 404 is raised.
            If an unexpected error occurs, an HTTPException with status code 500 is raised.
    """
    try:
        zone=zone.upper()
        zone_data = df[df['localita'] == zone]
        if zone_data.empty:
            raise HTTPException(status_code=404, detail=f"Unfortunately, the zone {zone} is not present in the dataset")
        socket_types = zone_data['infra'].unique().tolist()

        return f'In {zone} the type of socket is {socket_types}'
    except Exception as e:
        error_message= f'Unfortunately, the address {zone} is not present in the dataset'
        raise HTTPException(status_code=500, detail=error_message)


@app.get("/socket_types_by_zone/{zone}")
async def socket_types_by_zone(zone: str):
    return get_socket_types_by_zone(zone)


@app.get('/get-date')
def get_date():
    """
    Endpoint to get the current date.

    Returns:
        dict: Current date in ISO format.
    """
    current_date = datetime.now().isoformat()
    return JSONResponse(content={"date": current_date})
