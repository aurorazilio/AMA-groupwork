import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

"""
Execute this test by running on the terminal (from the app/) the command:
pytest --cov=app --cov-report=html tests/
 """

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

    
def test_street_name_exists():
    response12 = client.get("/module/search/CORSO INDIPENDENZA")
    excepted_response12 = "The provider for the charging station present in CORSO INDIPENDENZA is A2A Energy Solutions"
    assert response12.status_code == 200
    assert response12.json() == excepted_response12


def test_street_name_does_not_exist():
    response = client.get("/module/search/VIA CASALSERUGO")
    expected_error = "Unfortunately the street name you inserted is not present in our database"
    assert response.json() == expected_error


def test_provider_name_exists():
    response = client.get("/module/lookfor/Sorgenia")
    assert response.status_code == 200
    assert response.json() == [
        {
            'localita': 'Via algardi alessandro 4',
            'tipologia': 'N',
            'numero_pdr': '10'
        }
    ]

    
def test_provider_name_does_not_exist():
    response = client.get("/module/lookfor/pippo")
    assert response.json() == []
    

def test_numbers_of_stations_exists():
    response = client.get("/get_charging_stations/VIA LARGA")
    assert response.status_code == 200
    expected_response = "The number of charging stations in VIA LARGA is 3"
    assert response.json() == expected_response
    

def test_numbers_of_stations_does_not_exist():
    response = client.get("/get_charging_stations/NONEXISTENTSTREET")
    assert response.status_code == 200
    expected_error = {"error": f"The street 'NONEXISTENTSTREET' is not present in the dataset."}
    assert response.json() == expected_error
    

def test_socket_types_exists():
    response= client.get("/socket_types_by_zone/VIA LARGA 7")
    assert response.status_code == 200
    expected_response = "In VIA LARGA 7 the type of socket is ['AC Normal']"
    assert response.json() == expected_response
    

def test_socket_types_does_not_exist():
    response= client.get("/socket_types_by_zone/NONEXISTENTZONE")
    assert response.status_code == 500
    expected_error = {"Unfortunately, the street 'NONEXISTENTZONE' is not present in the dataset."}
    assert response.json() == expected_error


def test_addresses_exists():
    response = client.get("/addresses/DUOMO")
    assert response.status_code == 200

    expected_response = ["VIA LARGA","LARGO FRANCESCO RICHINI","VIA SANTA VALERIA","LARGO RAFFAELE MATTIOLI","PIAZZA EDISON TOMMASO ","VIA SANTA MARIA ALLA PORTA","VIA RASTRELLI","VIA CORRENTI CESARE","PIAZZA QUASIMODO SALVATORE","CORSO ITALIA","VIA SANTA MARIA FULCORINA","PIAZZA ERCULEA","FORO BUONAPARTE","VIA LENTASIO","VIA NEGRI GAETANO","VIA ARMORARI","VIA LARGA"]

    assert response.json() == expected_response


def test_addresses_does_not_exist():
    response = client.get("/addresses/NONEXISTENTAREA")
    assert response.status_code == 200
    assert response.json() == []


def test_case_insensitivity():
    response_1 = client.get("/module/lookfor/SoRgEnIa")
    response_2 = client.get("/module/lookfor/sorgenia")
    response_3 = client.get("/module/lookfor/SORGENIA")
    assert response_1.json() == response_2.json() == response_3.json()

    
def test_case_insensitivity_charg_points():
    response_1 = client.get("/get_charging_points/VIA LARGA")
    response_2 = client.get("/get_charging_points/via larga")
    response_3 = client.get("/get_charging_points/Via Larga")
    assert response_1.json() == response_2.json() == response_3.json()
    

def test_case_insensitivity_socket_types():
    response_1 = client.get("/socket_types_by_zone/ViA lArGa 7")
    response_2 = client.get("/socket_types_by_zone/via larga 7")
    response_3 = client.get("/socket_types_by_zone/VIA LARGA 7")
    assert response_1.json() == response_2.json() == response_3.json()
    
    
def test_case_insensitivity_street_name():
    response_1 = client.get("/module/search/ViALaRgA")
    response_2 = client.get("/module/search/VIALARGA")
    response_3 = client.get("/module/search/vialarga")
    assert response_1.json() == response_2.json() == response_3.json() 


def test_case_insensitivity_addresses():
    response_1 = client.get("/module/lookfor/DuOmO")
    response_2 = client.get("/module/lookfor/duomo")
    response_3 = client.get("/module/lookfor/DUOMO")
    assert response_1.json() == response_2.json() == response_3.json()