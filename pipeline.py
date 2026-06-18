import requests
import os
import logging
from typing import List, Dict, Any
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import pandas as pd
import ast



load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.weatherstack.com/current"

LOCATIONS = ["Abuja", "Akwa Ibom", "Kano", "Port Harcourt", "Lagos"]


def extract() -> List[Dict[str, Any]]:
    """
    Extracts weather data for specified locations from the Weatherstack API.

    Returns:
        A list of dictionaries containing weather data for each location.
    """
    weather_data_in_json = []
    
    # use a session for efficient persistent connections
    with requests.Session() as session:
        session.params = {'access_key': API_KEY} # set a default parameter for all requests
        
        for location in LOCATIONS:
            try:
                params = {'query': location}
                # make the API request using the session
                resp = session.get(BASE_URL, params=params)
                resp.raise_for_status() # raise an exception for HTTP errors
                data = resp.json()
                weather_data_in_json.append(data)
                
                logging.info(f"Successfully fetched weather data for {location}")
            except requests.exceptions.HTTPError as http_err:
                logging.error(f"HTTP error occurred for {location}: {http_err}")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Request error occurred for {location}: {req_err}")
            except ValueError:
                logging.error(f"Error parsing JSON response for {location}")
        return weather_data_in_json
            
      
      


def transform(weather_data_in_json: List[Dict[str, Any]]) -> str:
    """
    Transforms the extracted weather data into a list of cleaned, flat dictionaries.

    Args:
        weather_data_in_json: A list of dictionaries containing weather data for each location.

    Returns:
        A List of dictionaries containing of the weather data.
    """
    
    # Add this logic to handle the incoming string ast.literal_eval() will convert the string representation of a list of dictionaries into an actual list of dictionaries
    if isinstance(weather_data_in_json, str):
        print("DEBUG: Input is a string, attempting to evaluate as a python literal using ast.literal_eval()")
        try:
            # Use ast.literal_eval instead of json.loads to safely evaluate the string as a Python literal
            weather_data_in_json = ast.literal_eval(weather_data_in_json)
        except (ValueError, SyntaxError) as e:
            print(f"ERROR: Failed to evaluate string with ast.literal_eval: {e}")
            raise ValueError("Input string could not be evaluated as a Python literal")
        
    transformed_data = []
    
    for item in weather_data_in_json:
        # Check if the API returned an error payload(like the 4429 errors)
        if 'location' not in item:
            continue
        
        item = {
            "City": item['location']['name'],
            "Region": item['location']['region'],
            "Temperature": item['current']['temperature'],
            "Humidity": item['current']['humidity'],
            "Wind Degree": item['current']['wind_degree'],
            "Wind Speed (kph)": item['current']['wind_speed'],
            "Wind Direction": item['current']['wind_dir'],
            "Date": item['location']['localtime']
        }
        transformed_data.append(item)
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'transformed_data.pkl')
        
    # write the data to pickle file
    with open(file_path, 'wb') as f:
        pd.to_pickle(transformed_data, f)
        logging.info("Transformed data has been written to transformed_data.pkl")
            
    return file_path
    
    
    
    
def load(transformed_data_path: str) -> Optional[int]:
    """
    Loads the transformed weather data into a PostgreSQL database.

    Args:
        df: The pandas DataFrame to load

    Returns:
            The number of records inserted into the database, or None if an error occurred.
    """

    if isinstance(transformed_data_path, str):
        # Load the transformed data from the pickle fileq
        with open(transformed_data_path, 'rb') as f:
            transformed_data = pd.read_pickle(f)
            transformed_data = pd.DataFrame(transformed_data)
            print(transformed_data.head())
            logging.info(f" Loaded transformed data from {transformed_data_path}")
    else:
        logging.error("Invalid input: transformed_data_path should be a string path to the pickle file")
        return None
        
    conn_string: Optional[str] = os.getenv("DATABASE_URL")
    if not conn_string:
            logging.error("DATABASE_URL environment variable is not set")
            return None
        
    engine: Engine = create_engine(conn_string)
    rows_loaded = None
    try:
        # Use a context manager for reliable connection handling
        with engine.connect() as connection:
            logging.info("Successfully connected to the database")
                
            transformed_data.to_sql(
                name='daily_weather',
                con=connection,
                if_exists='append',
                index=False # Assuming your DataFrame index is not relevant for the database table
            )
            rows_loaded = len(transformed_data)
            logging.info(f"Successfully loaded {rows_loaded} records into the database")
                
    except Exception as e:
            logging.error(f"Error loading data into the database: {e}")
    return rows_loaded
    


def view_database_data():
    """Queries climians_db and prints the daily_weather table records."""
    conn_string = os.getenv("DATABASE_URL")
    if not conn_string:
        logging.error("DATABASE_URL is not configured.")
        return
        
    engine = create_engine(conn_string)
    query = "SELECT * FROM daily_weather;"
    
    try:
        with engine.connect() as connection:
            # Read the SQL table directly back into a Pandas DataFrame
            df = pd.read_sql(query, con=connection)
            
            print("\n=================== CLIMIANS_DB: DAILY_WEATHER ===================")
            if df.empty:
                print("The table exists but contains 0 records.")
            else:
                print(f"Total rows found: {len(df)}")
                print(df.to_string()) # to_string() ensures all columns show cleanly in the terminal
            print("==================================================================\n")
    except Exception as e:
        logging.error(f"Could not read from database: {e}")


    