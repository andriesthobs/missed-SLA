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
df['Month'] = pd.to_datetime(df['Month'], errors='coerce').dt.strftime('%b-%y')

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

pivot_table.columns = [f"{month} Missed" for month in sorted(pivot_table.columns, key=lambda x: pd.to_datetime(x, format='%b-%y'))]

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
##################################################################################################
import plotly.express as px

# Grouping and pivoting
df_grouped = df_selection.groupby(['Month', 'Customer Name']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Month', columns='Customer Name', values='Count').fillna(0)

fig = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns,
             title="Customer Missed Per Month",
             labels={'value': 'Count', 'index': 'Month'},
             barmode='stack')

fig.update_traces(showlegend=True, selector=dict(type='bar'))
fig.update_layout(legend=dict(traceorder='normal'))

fig.update_layout(
    clickmode='event+select'
)


##################################################################################################


###################################################################################################
st.markdown("-----------------------------------------------------")
df_grouped = df_selection.groupby(['Month', 'SIP created']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Month', columns='SIP created', values='Count').fillna(0)

figSIP = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns,
             title="SIP's created Per Month",
             labels={'value': 'Count', 'index': 'Month'},
             barmode='group')
###################################################################################################
colf1,colf2=st.columns(2)

with colf1:
    st.plotly_chart(fig)
with colf2:
    st.plotly_chart(figSIP)

####################################Credit Graph####################################################
df_grouped = df_selection.groupby(['Month', 'SIP created']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Month', columns='SIP created', values='Count').fillna(0)

figSIP = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns,
             title="SIP's created Per Month",
             labels={'value': 'Count', 'index': 'Month'},
             barmode='group')

#####################################Country Graph###################################################

df_grouped = df_selection.groupby(['Month', 'Credit']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Month', columns='Credit', values='Count').fillna(0)

figCred = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns,
             title="Credit created Per Month",
             labels={'value': 'Count', 'index': 'Month'},
             barmode='group')

#####################################################################################################

df_grouped = df_selection.groupby(['Month', 'Country']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='Month', columns='Country', values='Count').fillna(0)

figCount = px.bar(df_pivot, x=df_pivot.index, y=df_pivot.columns,
             title="Country Missed Per Month",
             labels={'value': 'Count', 'index': 'Month'},
             barmode='group')

#########################################################################################
st.markdown("-----------------------------------------------------")
ColCred,ColdCountry= st.columns(2)


with ColCred:

    st.plotly_chart(figCred)

with ColdCountry:
    st.plotly_chart(figCount)

st.markdown("-----------------------------------------------------")
with st.expander("Missed SLA Preview"):

    selected_month=st.multiselect('Select Month(s)',sorted(df['Month'].unique(), key=lambda x: pd.to_datetime(x, format='%b-%y')), format_func=lambda x: x)
    selected_smm=st.multiselect('Select SMM(s)',df['SMM'].unique())
    selected_sm=st.multiselect('Select SM(s)',df['Service Manager'].unique())

    filtered_df=df[
        (df['Month'].isin(selected_month)) &
        (df['SMM'].isin(selected_smm))&
        (df['Service Manager'].isin(selected_sm))
    ]
    st.dataframe(filtered_df) 
