import re
import numpy as np


# === Data Preprocessing and Transformation ===

# Converts Horsepower to RPM using a conversion factor.
def create_RPM_from_hp(horsepower):
    """
    Convert Horsepower to RPM.

    Args:
        horsepower (float): Value in Horsepower.

    Returns:
        float: Value in RPM (Revolutions Per Minute).
    """
    rpm = horsepower * 5252
    return rpm


# Checks if a given string contains non-numeric characters.
def contains_non_numeric(s):
    """
    Check if a string contains non-numeric characters.

    Args:
        s (str): Input string.

    Returns:
        bool: True if string contains non-numeric characters, False otherwise.
    """
    for char in s:
        if char.isdigit():
            return False
    return True


# Converts Torque to Newton Meters (Nm) based on units in the input.
def convert_to_Nm(torque):
    """
    Convert Torque to Newton Meters (Nm).

    Args:
        torque (str): Torque value with units.

    Returns:
        float: Value in Nm.
    """
    torque = re.sub(r'[ ]', '', torque)
    numeric_part = re.findall(r'[0-9]+\.?', torque)

    if 'lb' in torque.lower():
        torque_value = float(numeric_part[0]) * 1.356
    elif contains_non_numeric(torque):
        return np.nan
    else:
        torque_value = float(numeric_part[0])

    return round(torque_value, 2)


# Converts various horsepower units to standard horsepower.
def convert_to_hp(power):
    """
    Convert various horsepower units to standard horsepower.

    Args:
        power (str): Power value with units.

    Returns:
        float: Value in horsepower (hp).
    """
    power = re.sub(r'[ ]', '', power)
    numeric_part = re.findall(r'[0-9]+\.?', power)

    if 'kw' in power.lower():
        power_value = float(numeric_part[0]) * 1.34102209
    elif 'ps' in power.lower():
        power_value = float(numeric_part[0]) * 0.9863200706
    elif 'bhp' in power.lower():
        power_value = float(numeric_part[0]) * 13.1548
    elif 'w' in power.lower():
        power_value = float(numeric_part[0]) * 0.001341
    else:
        power_value = float(numeric_part[0])

    return round(power_value, 2)


# Converts various cubic centimeter units to standard cubic centimeters.
def convert_to_cc(volume):
    """
    Convert various cubic centimeter units to standard cubic centimeters (cc).

    Args:
        volume (str): Volume value with units.

    Returns:
        float: Value in cubic centimeters (cc).
    """
    volume = re.sub(r'[ ]', '', volume)
    numeric_part = re.findall(r'[0-9]+\.?[0-9]', volume)

    if 'kw' in volume.lower():
        volume_value = float(numeric_part[0]) * 11.3636
    elif contains_non_numeric(volume):
        return np.nan
    else:
        volume_value = float(numeric_part[0])

    return round(volume_value, 2)


# Converts Price in Indian Rupees (INR) to US Dollars (USD).
def convert_price_to_int(price):
    """
    Convert Price in Indian Rupees (INR) to US Dollars (USD).

    Args:
        price (str): Price value with units and symbols.

    Returns:
        float: Value in US Dollars (USD).
    """
    price = re.sub(r'[, ]', '', price)
    numeric_part = re.findall(r'[0-9]+\.?[0-9]*', price)

    if 'lakh' in price.lower():
        price_value = float(numeric_part[0]) * 100000
    elif 'crore' in price.lower():
        price_value = float(numeric_part[0]) * 10000000
    else:
        price_value = float(numeric_part[0])

    if '$' in price:
        return round(price_value, 2)
    else:
        return round(price_value * 0.014, 2)


# Retrieves the engine type based on the given engine name.
def get_engine_type(engine_name):
    """
    Get the engine type based on the given engine name.

    Args:
        engine_name (str): Name of the engine.

    Returns:
        str: Engine type ('electric' or 'petrol').
    """
    engine_name = engine_name.lower()

    if engine_name == 'electric':
        return 'electric'
    else:
        return 'petrol'


# Converts input to an integer, handling various formats.
def convert_to_integer(value):
    """
    Convert input to an integer, handling various formats.

    Args:
        value (str or int): Input value.

    Returns:
        int: Integer representation of the input.
    """
    try:
        return int(value)
    except ValueError:
        try:
            value = value.lower()
            if value in ['single', 'one']:
                return 1
            elif value in ['two', 'parallel-twin']:
                return 2
            elif value == 'three':
                return 3
            elif value == 'four':
                return 4
            else:
                return None
        except AttributeError:
            return None


# Groups body types based on common categorizations.
def group_body_type(body_type):
    """
    Group body types based on common categorizations.

    Args:
        body_type (str): Body type description.

    Returns:
        str: Grouped body type.
    """
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


# Groups bike looks based on common categorizations.
def group_bike_look(look):
    """
    Group bike looks based on common categorizations.

    Args:
        look (str): Bike look description.

    Returns:
        str: Grouped bike look.
    """
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


# Groups transmission types based on common categorizations.
def group_transmission_type(transmission_type):
    """
    Group transmission types based on common categorizations.

    Args:
        transmission_type (str): Transmission type description.

    Returns:
        str: Grouped transmission type.
    """
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
