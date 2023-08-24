import transform_functions as ts

def cleaning_and_transform(df_pre):
    """
    Cleans and transforms the input DataFrame, creating dimensions and fact table.

    Args:
        df_pre (pd.DataFrame): Input DataFrame with raw data.

    Returns:
        dict: A dictionary containing transformed dimensions and fact table.
    """
    # Rename columns for better readability
    df_pre.rename(columns={'Price (in INR)': 'price_usd'}, inplace=True)
    df_pre.rename(columns={'Engine Type': 'engine_type_name',
                           'Number of Cylinders': 'number_of_cylinders',
                           'Horsepower': 'horse_power_hp',
                           'Torque': 'torque_nm',
                           'Number of cc': 'cc'}, inplace=True)

    # Apply conversion functions to respective columns
    df_pre.horse_power_hp = df_pre.horse_power_hp.map(ts.convert_to_hp)
    df_pre.torque_nm = df_pre.torque_nm.map(ts.convert_to_Nm)
    df_pre.cc = df_pre.cc.map(ts.convert_to_cc)
    df_pre['rpm'] = df_pre.horse_power_hp.map(ts.create_RPM_from_hp)
    df_pre['price_usd'] = df_pre['price_usd'].map(ts.convert_price_to_int)
    df_pre['engine_type'] = df_pre.engine_type_name.map(ts.get_engine_type)
    df_pre['number_of_cylinders'] = df_pre.number_of_cylinders.map(ts.convert_to_integer)
    df_pre['Body Type'] = df_pre['Body Type'].map(ts.group_body_type)
    df_pre['Looks'] = df_pre.Looks.map(ts.group_bike_look)
    df_pre['manual_automat'] = df_pre['Transmission Type'].map(ts.group_transmission_type)

    # Get indices of rows with NaN values
    indices_with_nan = df_pre.loc[df_pre.isnull().any(axis=1)].index

    # Drop rows with NaN values
    df_pre.drop(indices_with_nan, inplace=True)

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

    return data
