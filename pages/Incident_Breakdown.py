import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Incident Breakdown Dashboard", page_icon=":bar_chart", layout="wide")

st.title("Incident Breakdown")
st.markdown("_v1.0.0_")

with st.sidebar:
    st.header("Incident Sheet")
    upload_file = st.file_uploader("Choose file")

if upload_file is None:
    st.info("Please upload a file through the configuration", icon="ℹ️")
    st.stop()

@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)
    return df

df = load_data(upload_file)

df['Opened'] = pd.to_datetime(df['Opened'], errors='coerce').dt.strftime('%Y-%m-%d')

st.sidebar.header("Please filter here :")

Company = st.sidebar.multiselect(
    "Select the Client",
    options=df["Company"].unique(),
)

Manager = st.sidebar.multiselect(
    "Select the S Manager",
    options=df["Manager"].unique(),  
)

if not Manager or not Company:
    st.info("Please select both a Client/Company and an S Manager to get started.")
    st.stop()

df_selection = df.query("Manager == @Manager and Company == @Company")

totalNoOfIncident = int(df["Company"].count())
totNoSM = int(df_selection["Company"].count())
incidentPerSM = (totNoSM / totalNoOfIncident) * 100

incC1, incC2, incPer = st.columns(3)

with incC1:
    st.subheader("Total Incidents per SMM")
    st.subheader(totalNoOfIncident)

with incC2:
    st.subheader("Total incident per SM")
    st.subheader(totNoSM)

with incPer:
    st.subheader("Percentage per SM")
    if totNoSM == 0:
        st.subheader("You cannot Divide by Zero")
    else:
        st.subheader("%.2f" % incidentPerSM + " % ")

st.markdown("-------------------------------")

pivot_table = df_selection.pivot_table(index='Opened', columns="Company", aggfunc='size', fill_value=0)
data = []
for column in pivot_table.columns:
    trace = go.Scatter(x=pivot_table.index, y=pivot_table[column], mode='lines+markers', name=column)
    data.append(trace)

layout = go.Layout(title="Incidents Count per day", xaxis=dict(title='Opened'), yaxis=dict(title='Count'))
fig2 = go.Figure(data=data, layout=layout)

##############################Incident Count#####################################
df_grouped = df_selection.groupby(['Company', 'Resolution code']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Company', columns='Resolution code', values='Count').fillna(0)

fig = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns, title="Incidents Count Per Customer", barmode='stack')

############################Priority####################################

df_grouped = df_selection.groupby(['Company', 'Priority']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Company', columns='Priority', values='Count').fillna(0)

fig3 = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns, title="Priority  Count Per Customer", barmode='stack')

##############################Company Incident Percentage##########################################
df_grouped = df_selection.groupby('Company').size().reset_index(name='Count')
df_grouped.reset_index(drop=True, inplace=True)

fig_pie = px.pie(df_grouped, names='Company', values='Count',
                 title="Incidents percentage by S Manager",
                 labels={'Company': 'Company', 'Count': 'Count'},
                 hover_data=['Count'],
                 hole=0.4)
fig_pie.update_traces(textposition='inside', textinfo='label+percent')

incCountPerDay, incCountPerCust = st.columns(2)
st.markdown("---------------------------------------------------------")
PrioPerCust, percPerCust = st.columns(2)
st.markdown("---------------------------------------------------------")

with incCountPerDay:
    st.plotly_chart(fig2)

with incCountPerCust:
    st.plotly_chart(fig)

with PrioPerCust:
    st.plotly_chart(fig3)

with percPerCust:
    st.plotly_chart(fig_pie)
