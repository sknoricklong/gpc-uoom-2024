import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

st.sidebar.markdown(
    "[Source of Data](https://gpcsup.com/)",
    unsafe_allow_html=True
)

# Setup the connection to Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account_gpc.json', scope)
client = gspread.authorize(creds)

# Open the spreadsheet and read data into a DataFrame
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GTklMV5aUuRFR6I65ojR2vN7djvy2SEMuYcWWyDLD7k/edit#gid=0')
worksheet = sheet.get_worksheet(0)  # assuming the data is in the first sheet
records = worksheet.get_all_records()

df = pd.DataFrame.from_records(records)

# Convert the Date column to datetime format and then to string format
df['Date'] = pd.to_datetime(df['Date']).dt.normalize().dt.strftime('%Y-%m-%d')

st.title('UOOM Daily Dashboard')
st.subheader('Sites Scanned and GPC Supporting Sites Over Time')

# Create a figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=df['Date'], y=df['Sites_Scanned'], name="Sites Scanned"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df['Date'], y=df['GPC_Supporting_Sites'], name="GPC Supporting Sites"),
    secondary_y=True,
)

# Add figure title
# fig.update_layout(
#     title_text="Sites Scanned and GPC Supporting Sites Over Time"
# )

# Set x-axis title
fig.update_xaxes(title_text="Date")

# Set y-axes titles
fig.update_yaxes(title_text="Sites Scanned", secondary_y=False)
fig.update_yaxes(title_text="GPC Supporting Sites", secondary_y=True)

# Display the Plotly figure in Streamlit
st.plotly_chart(fig)

# Display the DataFrame below the chart
st.dataframe(df)



