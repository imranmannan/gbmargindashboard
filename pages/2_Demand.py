from utilities import get_demand_forecast_DA_from_elexon
import streamlit as st
import plotly.express as px
import pandas as pd

st.write('# Demand')

df = get_demand_forecast_DA_from_elexon()
df['dt_local_str'] = (pd.to_datetime(df['StartTime'],utc=True)
    .dt.tz_convert('Europe/London')
    .dt.strftime('%H:%M %d-%b')
    )
fig = px.line(df, x='dt_local_str',y=['TransmissionSystemDemand','NationalDemand'],
title=f'Live Demand Forecast DA [published {df.PublishTime.max()}]')
st.plotly_chart(fig)