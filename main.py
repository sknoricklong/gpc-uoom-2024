

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# Setup the connection to Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_info = {
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["client_x509_cert_url"]
}
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
client = gspread.authorize(creds)

# Open the spreadsheet and read data into a DataFrame
sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{st.secrets["sheet_id"]}/edit#gid=0')
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
st.markdown('*Based on including an optional resource at https://domain.com/.well-known/gpc.json*')
# Create a figure for total sites and GPC supporting sites
fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# Calculate the ranges for y-axes dynamically
max_sites_scanned = max(df['Sites_Scanned'])
max_gpc_supporting = max(df['GPC_Supporting_Sites'])

# Set ranges to extend dynamically based on the maximum values observed
range_sites_scanned = [6.9e6, max_sites_scanned + 0.005 * max_sites_scanned]
range_gpc_supporting = [0, max_gpc_supporting + 0.1 * max_gpc_supporting]

# Normalize the range of 'GPC Supporting Sites' if needed to visually adjust scaling
if max_gpc_supporting / max_sites_scanned < 0.1:  # Example threshold ratio
    range_gpc_supporting = [0, max_sites_scanned * 0.1]  # Scale the secondary axis for better visual comparison

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

# Find the minimum and maximum values for 'GPC Supporting Sites' to set the axis range
min_gpc_supporting = min(df['GPC_Supporting_Sites'])
max_gpc_supporting = max(df['GPC_Supporting_Sites'])

# Adjust the secondary y-axis range to start from the minimum to just above the maximum
secondary_y_range = [min_gpc_supporting, max_gpc_supporting + 0.1 * max_gpc_supporting]

# Update the y-axis range for the secondary y-axis
fig1.update_yaxes(title_text="GPC Supporting Sites", secondary_y=True, range=secondary_y_range)

# Set y-axes titles
fig1.update_yaxes(title_text="Sites Scanned", secondary_y=False, range=range_sites_scanned)

# Add layout details for the first chart
fig1.update_layout(
    title_text="Sites Scanned and GPC Supporting Sites Over Time",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1,
        xanchor="left",
        x=0
    ),
    height=500,  # Smaller height for the first chart
    width=750
)


st.plotly_chart(fig1)

# Create a second figure for total percentage change from 7 days earlier
# Calculate 'Sites Scanned' 7 days ago for percentage calculation
df['Sites_Scanned_7_Days_Ago'] = df['Sites_Scanned'].shift(7)

# Calculate total percentage change from 7 days earlier for 'Sites Scanned'
df['Total_Percent_Change_Sites_Scanned'] = ((df['Sites_Scanned'] - df['Sites_Scanned_7_Days_Ago']) / df['Sites_Scanned_7_Days_Ago']) * 100

# Then proceed to add traces to fig2
fig2 = go.Figure()

# Add trace for the total percentage change in 'Sites Scanned'
fig2.add_trace(
    go.Scatter(x=df['Date'], y=df['Total_Percent_Change_Sites_Scanned'], name="Sites Scanned % Change")
)


# Add trace for the total percentage change in 'GPC Supporting Sites'
fig2.add_trace(
    go.Scatter(x=df['Date'], y=df['Total_Percent_Change_from_7_Days_Earlier'], name="GPC % Change")
)


# Update the layout for fig2
fig2.update_layout(
    title_text="Total Percentage Change from 7 Days Earlier",
    xaxis_title="Date",
    yaxis_title="Percentage Change (%)",
    height=500,
    width=950,
    xaxis_range=['2024-04-10', max(df['Date'])]  # Ensure the x-axis range starts from April 10,
)

# Display the plot
st.plotly_chart(fig2)

# Display the DataFrame below the charts
st.dataframe(df[['Date', 'Sites_Scanned', 'GPC_Supporting_Sites']])

st.markdown(
    "[Source of Data](https://gpcsup.com/)",
    unsafe_allow_html=True
)
