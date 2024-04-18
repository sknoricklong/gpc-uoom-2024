import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Setup the connection to Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account_gpc.json', scope)
client = gspread.authorize(creds)

# Open the spreadsheet and read data into a DataFrame
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GTklMV5aUuRFR6I65ojR2vN7djvy2SEMuYcWWyDLD7k/edit#gid=0')
worksheet = sheet.get_worksheet(0)  # assuming the data is in the first sheet
records = worksheet.get_all_records()

df = pd.DataFrame.from_records(records)

# Convert the Date column to datetime format
df['Date'] = pd.to_datetime(df['Date']).dt.normalize()

# Calculate GPC supporting sites 7 days ago for percentage calculation
df['GPC_Support_7_Days_Ago'] = df['GPC_Supporting_Sites'].shift(7)

# Calculate total percentage change from 7 days earlier
df['Total_Percent_Change_from_7_Days_Earlier'] = ((df['GPC_Supporting_Sites'] - df['GPC_Support_7_Days_Ago']) / df['GPC_Support_7_Days_Ago']) * 100

st.title('Daily Dashboard: GPC Awareness')

# Create a figure for total sites and GPC supporting sites
fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces for total sites and GPC supporting sites
fig1.add_trace(
    go.Scatter(x=df['Date'], y=df['Sites_Scanned'], name="Sites Scanned"),
    secondary_y=False,
)

fig1.add_trace(
    go.Scatter(x=df['Date'], y=df['GPC_Supporting_Sites'], name="GPC Supporting Sites"),
    secondary_y=True,
)

# Set x-axis title
fig1.update_xaxes(title_text="Date")

# Set y-axes titles
fig1.update_yaxes(title_text="Sites Scanned", secondary_y=False)
fig1.update_yaxes(title_text="GPC Supporting Sites", secondary_y=True)

# Add layout details
fig1.update_layout(
    title_text="Sites Scanned and GPC Supporting Sites Over Time",
    height=400
)

st.plotly_chart(fig1)

# Create a second figure for total percentage change from 7 days earlier
fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(x=df['Date'], y=df['Total_Percent_Change_from_7_Days_Earlier'], name="Total % Change from 7 Days Earlier", line=dict(color='green'))
)

fig2.update_layout(
    title_text="Total Percentage Change in GPC Supporting Sites from 7 Days Earlier",
    xaxis_title="Date",
    yaxis_title="Total Change from 7 Days Earlier (%)",
    height=400
)

st.plotly_chart(fig2)

# Display the DataFrame below the charts
st.dataframe(df[['Date', 'Sites_Scanned', 'GPC_Supporting_Sites']])

st.markdown(
    "[Source of Data](https://gpcsup.com/)",
    unsafe_allow_html=True
)
