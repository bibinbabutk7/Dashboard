import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Invoice", page_icon=":bar_chart:",layout="wide")
st.title(" :shopping_trolley: Payment Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\Users\Kooikmart\Desktop\InvoicePy")
    df = pd.read_csv("Supplierpayment2.csv", encoding = "ISO-8859-1")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Section
Section = st.sidebar.multiselect("Choose Category", df["Section"].unique())
if not Section:
    df2 = df.copy()
else:
    df2 = df[df["Section"].isin(Section)]

# Create for Supplier
Supplier = st.sidebar.multiselect("Choose Supplier", df2["Supplier"].unique())
if not Supplier:
    df3 = df2.copy()
else:
    df3 = df2[df2["Supplier"].isin(Supplier)]

# Create for Description
Description = st.sidebar.multiselect("Choose Product",df3["Description"].unique())

# Filter the data based on Section, Supplier and Description

if not Section and not Supplier and not Description:
    filtered_df = df
elif not Supplier and not Description:
    filtered_df = df[df["Section"].isin(Section)]
elif not Section and not Description:
    filtered_df = df[df["Supplier"].isin(Supplier)]
elif Supplier and Description:
    filtered_df = df3[df["Supplier"].isin(Supplier) & df3["Description"].isin(Description)]
elif Section and Description:
    filtered_df = df3[df["Section"].isin(Section) & df3["Description"].isin(Description)]
elif Section and Supplier:
    filtered_df = df3[df["Section"].isin(Section) & df3["Supplier"].isin(Supplier)]
elif Description:
    filtered_df = df3[df3["Description"].isin(Description)]
else:
    filtered_df = df3[df3["Section"].isin(Section) & df3["Supplier"].isin(Supplier) & df3["Description"].isin(Description)]

category_df = filtered_df.groupby(by = ["Supplier"], as_index = False)["Amount"].sum()

with col1:
    st.subheader("Supplier wise purchase")
    fig = px.bar(category_df, x = "Supplier", y = "Amount", text = ['AED {:,.2f}'.format(x) for x in category_df["Amount"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Category wise purchase")
    fig = px.pie(filtered_df, values = "Amount", names = "Section", hole = 0.5)
    fig.update_traces(text = filtered_df["Section"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Category_ViewData"):
        Section = filtered_df.groupby(by = "Section", as_index = False)["Amount"].sum()
        st.write(Section.style.background_gradient(cmap="Oranges"))
        csv = Section.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Section.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
        
filtered_df["day"] = filtered_df["Order Date"].dt.to_period("D")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["day"].dt.strftime("%Y-%m-%d"))["Amount"].sum()).reset_index()
fig2 = px.line(linechart, x = "day", y="Amount", labels = {"Amount": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create a treem based on Section, category, Status
st.subheader("Hierarchical view of Amount using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Section","Supplier","Status"], values = "Amount",hover_data = ["Amount"],
                  color = "Status")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Description wise purchase')
    fig = px.pie(filtered_df, values = "Amount", names = "Section", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Description"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Supplier wise purchase')
    fig = px.pie(filtered_df, values = "Amount", names = "Section", template = "gridon")
    fig.update_traces(text = filtered_df["Supplier"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Status Amount Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Section","Supplier","Description","Invoice ID","Amount"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Status Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Amount", index = ["Status"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Amount")
data1['layout'].update(title="Relationship between Amount using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Amount",titlefont=dict(size=19)),
                       yaxis = dict(title = "Purchase", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")