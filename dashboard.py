import pandas
import streamlit as st
import plotly.express as px
st.set_page_config(layout="wide")
# Load data into pandas dataframe
worker_data: pandas.DataFrame = pandas.read_csv('./worker.csv')
bonus_data: pandas.DataFrame = pandas.read_csv('./bonus.csv')
title_data: pandas.DataFrame = pandas.read_csv('./title.csv')

# Total Earnings Per Department
total_bonus = bonus_data.groupby("WORKER_REF_ID")["BONUS_AMOUNT"].sum().reset_index()
total_bonus.columns = ["WORKER_REF_ID", "TOTAL_BONUS"]
worker_earn = worker_data.merge(right=total_bonus, left_on="WORKER_ID", right_on="WORKER_REF_ID", how="left")
worker_earn["TOTAL_BONUS"] = worker_earn["TOTAL_BONUS"].fillna(0) # Safer than worker_earn["TOTAL_BONUS"].fillna(0, inplace=True)
worker_earn["TOTAL_EARN"] = worker_earn["SALARY"] + worker_earn["TOTAL_BONUS"]
# worker_earn
dept_earn = worker_earn.groupby("DEPARTMENT")["TOTAL_EARN"].sum().reset_index()
dept_earn.columns = ["DEPARTMENT", "TOTAL_EARN"]
# dept_earn.plot(kind="bar", x="DEPARTMENT")
dept_earn_plt = px.bar(dept_earn, "DEPARTMENT", "TOTAL_EARN", title="Total Earnings per Department") # Fig

# Worker Title Dataframe
worker_title = worker_data.merge(right=title_data, left_on="WORKER_ID", right_on="WORKER_REF_ID", how="left")
worker_title["WORKER_TITLE"] = worker_title["WORKER_TITLE"].fillna("Executive")
worker_title = worker_title.sort_values(by=["DEPARTMENT", "WORKER_TITLE"])
# worker_title

# Average Salary Per Title in each Department
average_title_salary = worker_title.groupby(["DEPARTMENT", "WORKER_TITLE"])["SALARY"].mean().reset_index()
average_title_salary.columns = ["DEPARTMENT", "TITLE", "AVERAGE_SALARY"]
# average_title_salary

# Get total worker per department
total_worker_per_department = worker_title.groupby(["DEPARTMENT", "WORKER_TITLE"])["WORKER_ID"].count().reset_index()
total_worker_per_department.columns = ["DEPARTMENT", "TITLE", "TOTAL"]
# total_worker_per_department

# fig = px.scatter(data_frame=worker_title, x=["DEPARTMENT","WORKER_TITLE"], y="SALARY", color="SALARY", color_continuous_scale="reds")
fig = px.scatter(data_frame=worker_title,
                 title="Salary Per Title",
                 x="WORKER_TITLE",  # Use WORKER_TITLE for x-axis
                 y="SALARY",  # Use SALARY for y-axis,
                 labels={"SALARY": "Salary", "WORKER_TITLE": "Position"},
                 color="SALARY",  # Color by salary
                 color_continuous_scale="reds")
tab1, tab2 = st.tabs(["Salary/Title", "Dataframe"])
tab1.plotly_chart(fig)
tab2.dataframe(worker_title)
# streamlit display
cols = st.columns((1, 1, 1), gap='medium') # ref https://github.com/dataprofessor/population-dashboard/blob/master/streamlit_app.py

with cols[0]:
    cols2 = st.columns((1, 1), gap="small")
    with cols2[0]:
        st.metric("Fixed Expense Per Year", f"{worker_data['SALARY'].sum():,.2f}", border=True)
    with cols2[1]:
        st.metric("Fixed Expense Per Month", f"{worker_data['SALARY'].sum()/12:,.2f}", border=True)

    st.markdown("#### Total Earnings Per Department")
    st.dataframe(dept_earn.sort_values(by=['TOTAL_EARN'], ascending=False), column_order=("DEPARTMENT", "TOTAL_EARN"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "DEPARTMENT": st.column_config.TextColumn(
                        "Department",
                    ),
                    "TOTAL_EARN": st.column_config.ProgressColumn(
                        "Total Earning",
                        format="%f",
                        min_value=0,
                        max_value=max(dept_earn["TOTAL_EARN"]),
                     )})
    
with cols[1]:
    st.markdown("#### Average Salary Per Position")
    st.bar_chart(average_title_salary, x="TITLE", y="AVERAGE_SALARY", color="DEPARTMENT", stack=False, x_label="Average Salary", y_label="Title")

with cols[2]:
    st.markdown("#### Total Worker Per Department")
    st.bar_chart(total_worker_per_department, x="DEPARTMENT", y="TOTAL", stack=False, color="TITLE", horizontal=True)

    


