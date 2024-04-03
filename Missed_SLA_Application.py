
import plotly.validators.surface
from plotly.validators import surface
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

st.set_page_config(page_title="Missed SLA Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Missed SLA Dashboard")
st.markdown("_v1.1.0_")

with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is None:
    st.info(" Upload a file through config", icon="ℹ️")
    st.stop()

@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)
    return df

df = load_data(uploaded_file)

# Convert the date format to 'Mon-YY'
df['Month'] = pd.to_datetime(df['Month']).dt.strftime('%b-%y')

with st.expander("Data Preview"):
    st.dataframe(df)

# Sidebar
st.sidebar.header("Please filter here :")

SMM = st.sidebar.multiselect(
    "Select the SMM :",
    options=df["SMM"].unique(),
    default=df["SMM"].unique()
)

Month = st.sidebar.multiselect(
    "Select the Month :",
    options=df["Month"].unique().tolist(),
    default=df["Month"].unique().tolist()
)

# Display message if no selections are made
if not SMM or not Month:
    st.info("Please select SMM and Month to get started.")
    st.stop()

df_selection = df.query("SMM == @SMM and Month == @Month")

# ----Main Page-----

Missed_Reason = int(df_selection["Month"].count())
Missed_Reason1 = int(df["Missed Reason"].count())
Missed_per__SMM = (Missed_Reason / Missed_Reason1) * 100

col1, col2= st.columns(2)

with col1:
    st.subheader("No of Missed SLA")
    st.subheader(Missed_Reason1)

with col2:
    st.subheader("No of Missed SLA per SMM")
    st.subheader(Missed_Reason)

st.markdown("-------------------------------")
################################################################################################
pivot_table = df_selection.pivot_table(index='Month', columns='SMM', aggfunc='size', fill_value=0)
data = []
for column in pivot_table.columns:
    trace = go.Scatter(x=pivot_table.index, y=pivot_table[column], mode='lines+markers', name=column)
    data.append(trace)

# Layout settings
layout = go.Layout(title="Root cause per SMM",
                    xaxis=dict(title='Month'),
                    yaxis=dict(title='Count'))
# Create line graph figure
fig2 = go.Figure(data=data, layout=layout)
#st.plotly_chart(fig)

################################################################################################
df_grouped = df_selection.groupby(['Month', 'Missed Reason']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Month', columns='Missed Reason', values='Count').fillna(0)

fig = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns,
             title="Missed Reasons Per Month",
             labels={'value': 'Count', 'index': 'Month'},
             barmode='stack')

#################################################################################################

df_grouped = df_selection.groupby('SMM').size().reset_index(name='Count')
df_grouped.reset_index(drop=True, inplace=True)

fig_pie = px.pie(df_grouped, names='SMM', values='Count',
                 title="Missed Reasons percentage by SMM",
                 labels={'SMM': 'SMM', 'Count': 'Count'},
                 hover_data=['Count'],
                 hole=0.4)
fig_pie.update_traces(textposition='inside', textinfo='label+percent')

#################################################################################################

pivot_table = df.pivot_table(index='Missed Reason', columns='Month', aggfunc='size', fill_value=0)

pivot_table.columns = [f"{month} Missed" for month in pivot_table.columns]

pivot_table.reset_index(inplace=True)
pivot_table = pivot_table.iloc[:, 0:]

styled_table = pivot_table.style \
    .set_table_styles([{'selector': 'th', 'props': [('background-color', 'red'), ('color', 'white')]}])\
    .set_properties(**{'text-align': 'center'}) \
    .set_caption("Missed Reasons by Month")

#st.subheader("Missed SLA by Root Cause")
#st.write(styled_table)

#################################################################################################
fr1,fr2=st.columns(2)

with fr1:
    st.subheader("Missed SLA by Root cause")
    st.write(styled_table)

with fr2:
    st.subheader("Root Cause per SMM Count")
    st.plotly_chart(fig2)

#################################################################################################

st.markdown("-----------------------------------------------------")

f1, f2 = st.columns(2)

with f1:
    st.subheader("SM Missed SLA")
    st.plotly_chart(fig)

with f2:
    st.subheader("Missed Reasons percentage by SMM")
    st.plotly_chart(fig_pie)

st.markdown("-----------------------------------------------------")
