import pandas as pd
# from tqdm.notebook import tqdm
# from stqdm import stqdm as tqdm
from entsoe import EntsoePandasClient
from typing import Iterable
import streamlit as st

# Define your ENTSOE API key
try:
    ENTSOE_API_KEY: str = st.secrets['ENTSOE_API_KEY']
except FileNotFoundError: # horrific pwd mgmt ik lol
    with open('ENTSOE_API_KEY.txt','r') as file:
        ENTSOE_API_KEY:str = file.read()


# Create an ENTSOE client using your API key
entsoe_client = EntsoePandasClient(api_key=ENTSOE_API_KEY)

# Define a function to get IC flows from ENTSOE
@st.cache_data
def get_IC_flows_from_ENTSOE(
    start_local_dt_str: str,
    end_local_dt_str: str,
    IC_country_code_list: Iterable[str] = ['FR', 'NL', 'BE', 'NO_2','GB_NIR','IE_SEM'],
    dayahead: bool = False
):
    """
    Get IC flows from ENTSOE for specified countries and time range.

    Args:
        start_local_dt_str (str): Start date and time in 'YYYY-MM-DD HH:mm' format.
        end_local_dt_str (str): End date and time in 'YYYY-MM-DD HH:mm' format.
        IC_country_code_list (Iterable[str], optional): List of country codes. Defaults to ['FR', 'NL', 'BE', 'NO_2'].
        dayahead (bool, optional): Whether to fetch day-ahead commercial schedules only, or incude within day. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame containing IC flows data.
    """

    # Convert input strings to timestamps with a specified timezone
    start = pd.Timestamp(start_local_dt_str, tz='Europe/London')
    end = pd.Timestamp(end_local_dt_str, tz='Europe/London')

    exports: pd.DataFrame = pd.DataFrame()
    imports: pd.DataFrame = pd.DataFrame()

    # Loop through the specified country codes to fetch import and export data
    for country in IC_country_code_list:
        imports[f"{country}"] = entsoe_client.query_scheduled_exchanges(
            country_code_from=country,
            country_code_to='GB',
            start=start,
            end=end,
            dayahead=dayahead
        )
        exports[f"{country}"] = entsoe_client.query_scheduled_exchanges(
            country_code_from='GB',
            country_code_to=country,
            start=start,
            end=end,
            dayahead=dayahead
        )

    # Unstack the data and prepare DataFrames for imports and exports
    imports.index = imports.index.tz_convert('Europe/London')
    imports = imports.unstack().reset_index().rename(
        columns={'level_0': "country", 'level_1': 'local_dt', 0: 'MW'}
    )
    imports['direction'] = 'import'

    exports = exports.unstack().reset_index().rename(
        columns={'level_0': "country", 'level_1': 'local_dt', 0: 'MW'}
    )
    exports['MW'] = exports['MW'] * -1
    exports['direction'] = 'export'

    # Concatenate import and export DataFrames to create the final DataFrame
    df = pd.concat([imports, exports], axis=0)

    # REMOVED Calculate net flows for each country at each timestamp
    # net = df.groupby(['country', 'local_dt'])[['MW']].sum().reset_index()
    # net['direction'] = 'net'
    # df = pd.concat([df, net], axis=0)

    # Format the local time as 'HH:MM'
    df['time_str'] = df['local_dt'].dt.strftime('%H:%M')

    return df

# # Get IC flows data for a specific time range
# start_time = '2023-10-16 17:00'
# end_time   = '2023-10-16 18:00'
# df = get_IC_flows_from_ENTSOE(start_time, end_time)
# You can now work with the 'df' DataFrame for further analysis or visualization.

