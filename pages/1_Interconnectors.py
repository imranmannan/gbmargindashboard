import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from utilities import get_IC_flows_from_ENTSOE
import pandas as pd

# choose date
event_date_str = st.date_input(
    "Choose Date",
    key='event_date_str',
    value=(pd.Timestamp.today() - pd.Timedelta(days=1)).date(),
    )
# event_date_str = '2023-09-26'

st.write('# Scheduled IC Flows')
# get IC flows
peak_start_str = str(event_date_str) + ' 17:00'
peak_end_str = str(event_date_str) + ' 18:00' # inclusive, hourly data 
df = get_IC_flows_from_ENTSOE(peak_start_str,peak_end_str)

# create plotly fig
net_total_df = df.groupby(['local_dt','time_str'],as_index=False)[['MW']].sum()
net_total_df['country']   = 'total'
net_total_df['direction'] = 'net'

# plot overall GB position
tp1 = pd.concat([df,net_total_df], axis=0)
fig1 = px.bar(tp1,y='MW',x='direction',color='country', barmode='stack', facet_col='time_str',title=f'{event_date_str}: Net IC Flows during Peak')
fig1.for_each_annotation(lambda a: a.update(text=a.text.replace("time_str=", ""))) # can make niceer with regex

st.plotly_chart(fig1)

# plot position per IC
fig2 = px.bar(df, x='country',y='MW',facet_col='time_str', color='country', barmode='stack', title=f'{event_date_str}: IC Flows per IC during Peak')
fig2.for_each_annotation(lambda a: a.update(text=a.text.replace("time_str=", ""))) # can make niceer with regex
st.plotly_chart(fig2)

# net_total_df
# # net_total_df
# df.groupby(['local_dt'],as_index=False)['MW'].sum()
# st.write(df)
