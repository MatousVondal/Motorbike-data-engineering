import re
import numpy as np
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import io
import requests

# Path to the CSV file
url = 'https://storage.googleapis.com/bike_analysis_vondal/bikes_data.csv'
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), sep=',')

df_pre = df

# _____________ PRE-Processing and data transformation __________________

# Function to convert Horsepower to RPM
def create_RPM_from_hp(value):
    rpm = value * 5252
    return rpm

# Function to check if a string contains non-numeric characters
def contains_non_numeric(string):
    for char in string:
        if char.isdigit():
            return False
    return True

# Function to convert Torque to Nm
def convert_to_Nm(value):
    # Remove dots and spaces
    value = re.sub(r'[ ]', '', value)

    # Extract the numeric part
    numeric_part = re.findall(r'[0-9]+\.?', value)

    if 'lb' in value.lower():
        numeric_value = float(numeric_part[0]) * 1.356
    elif contains_non_numeric(value):
        return np.nan
    else:
        numeric_value = float(numeric_part[0])

    return round(float(numeric_value), 2)

# Function to convert Horsepower to hp
def convert_to_hp(value):
    # Remove dots and spaces
    value = re.sub(r'[ ]', '', value)

    # Extract the numeric part
    numeric_part = re.findall(r'[0-9]+\.?', value)

    if 'kw' in value.lower():
        numeric_value = float(numeric_part[0]) * 1.34102209
    elif 'ps' in value.lower():
        numeric_value = float(numeric_part[0]) * 0.9863200706
    elif 'bhp' in value.lower():
        numeric_value = float(numeric_part[0]) * 13.1548
    elif 'w' in value.lower():
        numeric_value = float(numeric_part[0]) * 0.001341
    else:
        numeric_value = float(numeric_part[0])

    return round(float(numeric_value), 2)

# Function to convert Number of cc to cc
def convert_to_cc(value):
    # Remove dots and spaces
    value = re.sub(r'[ ]', '', value)

    # Extract the numeric part
    numeric_part = re.findall(r'[0-9]+\.?[0-9]', value)

    if 'kw' in value.lower():
        numeric_value = float(numeric_part[0]) * 11.3636
    elif contains_non_numeric(value):
        return np.nan
    else:
        numeric_value = float(numeric_part[0])

    return round(float(numeric_value), 2)

# Function to convert Price (in INR) to USD
def convert_price_to_int(price):
    # Remove commas and spaces
    price = re.sub(r'[, ]', '', price)

    # Extract the numeric part
    numeric_part = re.findall(r'[0-9]+\.?[0-9]*', price)

    # Check for lakhs or crore units
    if 'lakh' in price.lower():
        numeric_value = float(numeric_part[0]) * 100000
    elif 'crore' in price.lower():
        numeric_value = float(numeric_part[0]) * 10000000
    else:
        numeric_value = float(numeric_part[0])

    # Check for currency symbols
    if '$' in price:
        return round(float(numeric_value), 2)
    else:
        return round(float(numeric_value * 0.014), 2)


def get_engine_type(engine_name):
    engine_name = engine_name.lower()

    if engine_name in 'electric':
        return 'electric'
    else:
        return 'petrol'


def convert_to_integer(num_cylinders):
    try:
        return int(num_cylinders)
    except ValueError:
        try:
            num_cylinders = num_cylinders.lower()
            if num_cylinders == 'single' or num_cylinders == 'one':
                return 1
            elif num_cylinders == 'two' or num_cylinders == 'parallel-twin':
                return 2
            elif num_cylinders == 'three':
                return 3
            elif num_cylinders == 'four':
                return 4
            else:
                return None
        except AttributeError:
            return None


def group_body_type(body_type):
    body_type = body_type.lower()

    if body_type in ['naked', 'street naked', 'naked bike', 'naked streetfighter', 'street', 'standard', 'retro']:
        return 'Naked/Cruiser Style'
    elif body_type in ['racing', 'sport', 'sportbike', 'superbike', 'sports', 'supersport', 'sport touring',
                       'sports bike', 'sports naked', 'streetfighter']:
        return 'Sport/Sportbike Style'
    elif body_type in ['adventure', 'adventure touring', 'adventure bike', 'dual-sport', 'trail', 'adventure tourer']:
        return 'Adventure/Off-road Style'
    elif body_type in ['cruiser', 'roadster', 'tourer', 'touring']:
        return 'Touring Style'
    elif body_type in ['scrambler', 'street scrambler', 'tracker']:
        return 'Scrambler/Tracker Style'
    else:
        return 'Other-body-type'


def group_bike_look(look):
    look = look.lower()

    if look in ['sport', 'sporty', 'race-inspired', 'aggressive', 'modern, sporty', 'bold', 'sleek', 'modern, stylish',
                'modern, aggressive', 'modern, muscular', 'bold, aggressive', 'modern, aggressive', 'retro-modern',
                'sharp', 'stylish', 'urban']:
        return 'Sporty/Aggressive Look'
    elif look in ['adventure', 'touring', 'modern, rugged', 'modern, off-road', 'adventure, touring',
                  'adventure, sporty']:
        return 'Adventure/Touring Look'
    elif look in ['classy', 'classic', 'retro', 'classic, rugged', 'classic, bobber', 'classic, stylish',
                  'classic, vintage', 'retro, classic', 'retro-inspired']:
        return 'Classic/Retro Look'
    elif look in ['cruiser', 'classy, cruiser', 'fun', 'budget']:
        return 'Cruiser Look'
    elif look in ['practical', 'simple, reliable']:
        return 'Practical/Reliable Look'
    elif look in ['motocross', 'enduro', 'dirt']:
        return 'Off-road/Dirt Look'
    else:
        return 'Other-Look'


def group_transmission_type(transmission_type):
    transmission_type = transmission_type.lower()

    if transmission_type in ['6-speed quickshifter', '6-speed manual', 'manual', '6-speed sequential manual',
                             '6-speed automatic', '6-speed', 'six-speed sequential', 'six-speed',
                             'constant mesh, 6-speed', '4-speed constant mesh', '5-speed constant mesh',
                             '6-speed constant mesh', '5-speed', '4-speed', '6-speed manual', '5-speed manual',
                             '4-speed manual', 'six-speed constant mesh', '6 speed manual', '6-speed']:
        return 'Manual'
    elif transmission_type in ['cvt', 'cvt automatic', 'automatic']:
        return 'Automatic'
    else:
        return None


# Rename columns for better readability
df_pre.rename(columns={'Price (in INR)': 'price_usd'}, inplace=True)
df_pre.rename(columns={'Engine Type': 'engine_type_name',
                       'Number of Cylinders': 'number_of_cylinders',
                       'Horsepower': 'horse_power_hp',
                       'Torque': 'torque_nm',
                       'Number of cc': 'cc'}, inplace=True)

# Apply conversion functions to respective columns
df_pre.horse_power_hp = df_pre.horse_power_hp.map(convert_to_hp)
df_pre.torque_nm = df_pre.torque_nm.map(convert_to_Nm)
df_pre.cc = df_pre.cc.map(convert_to_cc)
df_pre['rpm'] = df_pre.horse_power_hp.map(create_RPM_from_hp)
df_pre['price_usd'] = df_pre['price_usd'].map(convert_price_to_int)
df_pre['engine_type'] = df_pre.engine_type_name.map(get_engine_type)
df_pre['number_of_cylinders'] = df_pre.number_of_cylinders.map(convert_to_integer)
df_pre['Body Type'] = df_pre['Body Type'].map(group_body_type)
df_pre['Looks'] = df_pre.Looks.map(group_bike_look)
df_pre['manual_automat'] = df_pre['Transmission Type'].map(group_transmission_type)

# Get indices of rows with NaN values
#indices_with_nan = df_pre.loc[df_pre.isnull().any(axis=1)].index

# Drop rows with NaN values
#df_pre.drop(indices_with_nan, inplace=True)

# Remove duplicate rows and reset the index
df_pre = df_pre.drop_duplicates().reset_index(drop=True)
df_pre['bike_id'] = df_pre.index

# Create the engine_type_dim DataFrame
engine_type_dim = df_pre[['engine_type_name','engine_type', 'number_of_cylinders', 'horse_power_hp',
                      'torque_nm','cc', 'rpm']].reset_index(drop=True)
engine_type_dim['engine_type_id'] = engine_type_dim.index
engine_type_dim = engine_type_dim[['engine_type_id','engine_type_name','engine_type', 'number_of_cylinders',
                                  'horse_power_hp', 'torque_nm', 'cc', 'rpm']]

# Create the company_dim DataFrame
company_dim = df_pre[['Company', 'Country of Origin']].reset_index(drop=True)
company_dim['company_id'] = company_dim.index
company_dim.rename(columns={'Company': 'company_name',
                            'Country of Origin': 'country_name'}, inplace=True)

# Map continents based on country
continents = []
for country in company_dim['country_name']:
    if country in ['Italy', 'Germany', 'Austria', 'United Kingdom', 'Sweden',
                   'UK', 'Spain', 'France', 'Denmark']:
        continents.append('Europe')
    elif country in ['United States', 'USA', 'Canada']:
        continents.append('North America')
    else:
        continents.append('Asia')

pd.options.mode.chained_assignment = None

# Update country names for UK and USA
uk = company_dim['country_name'][(company_dim.country_name == 'United Kingdom')].index.to_list()
us = company_dim['country_name'][(company_dim.country_name == 'United States')].index.to_list()

for i in uk:
    company_dim['country_name'][i] = 'UK'

for i in us:
    company_dim['country_name'][i] = 'USA'

# Add the continent column to company_dim DataFrame
company_dim['continent_name'] = continents
company_dim = company_dim[['company_id', 'company_name', 'country_name', 'continent_name']]

# Rename columns for better readability
df_pre.rename(columns={'Model': 'model_name',
                       'Year': 'year'}, inplace=True)

# Create the transmission_type_dim DataFrame
transmission_type_dim = df_pre[['Transmission Type', 'manual_automat']].reset_index(drop=True)
transmission_type_dim['transmission_type_id'] = transmission_type_dim.index
transmission_type_dim.rename(columns = {'Transmission Type':'transmission_type_name'}, inplace = True)
transmission_type_dim = transmission_type_dim[['transmission_type_id','transmission_type_name','manual_automat']]

# Create the drive_train_dim DataFrame
drive_train_dim = df_pre[['Drivetrain']].reset_index(drop=True)
drive_train_dim['drive_train_id'] = drive_train_dim.index
drive_train_dim.rename(columns={'Drivetrain': 'drive_train_name'}, inplace=True)
drive_train_dim = drive_train_dim[['drive_train_id', 'drive_train_name']]

# Create the body_type_dim DataFrame
body_type_dim = df_pre[['Body Type', 'Number of Seating', 'Looks']].reset_index(drop=True)
body_type_dim['body_type_id'] = body_type_dim.index
body_type_dim.rename(columns={'Body Type': 'body_type_name',
                              'Number of Seating': 'number_of_seating',
                              'Looks': 'looks'}, inplace=True)
body_type_dim = body_type_dim[['body_type_id', 'body_type_name', 'number_of_seating', 'looks']]

# Create the fact_table DataFrame by merging all dimensions and selecting relevant columns
fact_table = df_pre.merge(company_dim, left_on='bike_id', right_on='company_id') \
                    .merge(transmission_type_dim, left_on='bike_id', right_on='transmission_type_id') \
                    .merge(drive_train_dim, left_on='bike_id', right_on='drive_train_id') \
                    .merge(engine_type_dim, left_on='bike_id', right_on='engine_type_id') \
                    .merge(body_type_dim, left_on='bike_id', right_on='body_type_id') \
                    [['bike_id', 'company_id', 'transmission_type_id', 'drive_train_id',
                      'engine_type_id', 'body_type_id', 'model_name', 'price_usd', 'year']]

# Create a dictionary to store the tables as JSON
data = {
    "company_dim": company_dim.to_dict(orient="dict"),
    "transmission_type_dim": transmission_type_dim.to_dict(orient="dict"),
    "drive_train_dim": drive_train_dim.to_dict(orient="dict"),
    "engine_type_dim": engine_type_dim.to_dict(orient="dict"),
    "body_type_dim": body_type_dim.to_dict(orient="dict"),
    "fact_table": fact_table.to_dict(orient="dict")
}





