import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="EduRisk Analytics - Lab 05",
    page_icon="🎓",
    layout="wide"
)

def load_student_data():
    try:
        data = pd.read_csv("students.csv")
        return data
    except FileNotFoundError:
        st.error(
            "students.csv was not found. Please place it in the same folder as app.py."
        )
        st.stop()

#laod the student data
student_df = load_student_data()
#added custom css


st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #F1F5F9;
}

/* Main content */
.block-container {
    padding-top: 2rem;
    max-width: 1300px;
}

/* Headings */
h1, h2, h3 {
    color: #0F172A !important;
}

/* Normal text */
.stApp p, .stApp label, .stApp span {
    color: #334155;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0F172A;
    border-right: 1px solid #1E293B;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* Sidebar title */
section[data-testid="stSidebar"] h1 {
    color: #FFFFFF;
    border-bottom: 3px solid #3B82F6;
    padding-bottom: 10px;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 4px solid #2563EB;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

div[data-testid="stMetricLabel"] * {
    color: #64748B !important;
}

div[data-testid="stMetricValue"] * {
    color: #0F172A !important;
}

/* Form */
div[data-testid="stForm"] {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background-color: #2563EB;
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #1D4ED8;
}

/* Data table */
div[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Hide Streamlit menu and footer */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# risk level function 
def get_risk_level(score, attendance):
    if score < 60 or attendance < 60:
        return "High Risk"
    elif score < 75 or attendance < 75:
        return "Medium Risk"
    else:
        return "Low Risk"

#add the risk level column
student_df["Risk Level"] = student_df.apply(
    lambda row: get_risk_level(
        row["Score"],
        row["Attendance"]
    ),
    axis=1
)

# 6. DESIGN: RISK LEVEL COLOURS
# green = Low, yellow = Medium, red = High
risk_colors = {
    "Low Risk": "background-color: #DCFCE7; color: #166534",
    "Medium Risk": "background-color: #FEF3C7; color: #92400E",
    "High Risk": "background-color: #FEE2E2; color: #991B1B"
}

# DESIGN: paint only the "Risk Level" column of a table
def color_risk(df):
    return df.style.map(
        lambda value: risk_colors.get(value, ""),
        subset=["Risk Level"]
    )
# session state
if "risk_history" not in st.session_state:
    st.session_state["risk_history"] = []

total_students = len(student_df)
average_score = student_df["Score"].mean()
average_attendance = student_df["Attendance"].mean()
low_score_students = student_df[student_df["Score"] < 60].shape[0]

#sidebar menu
with st.sidebar:
    st.title("EduRisk Menu")
    selected_page = st.radio(
        "Select Page",
        ["Home", "Dashboard", "Student Data", "Risk Checker", "About"]
    )


#Home Page
if selected_page == "Home":
    st.title("🎓 EduRisk Analytics")
    st.subheader("Interactive Dashboard with Visualization and Filters")
    st.write("Welcome to Lab 05.")
    st.write(
        "In this lab, the app improves the Dashboard page using "
        "grouped summaries, interactive filters, Streamlit charts, and Plotly charts."
    )
    st.success("Lab 05 app is running successfully!")
    
#Dashboard Page
elif selected_page == "Dashboard":
    st.title("Interactive Student Performance Dashboard")

    st.write(
         "Use filters to explore student performance by course, risk level, "
        "and attendance. The dashboard updates based on your selections."
    )
    # Dashboard filters
    st.subheader("Dashboard Filters")
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    # Add Course filters 
    with filter_col1:
        course_options = ["All"] + sorted(student_df["Course"].unique())
        selected_course = st.selectbox(
            "Filter by Course",
            course_options
        )
    # Add risk level filter
    with filter_col2:
        risk_options = ["All"] + sorted(student_df["Risk Level"].unique())
        selected_risk = st.selectbox(
            "Filter by Risk Level",
            risk_options
        )
    # Add attendent slider
    with filter_col3:
        minimum_attendance = st.slider(
            "Minimum Attendance",
            0,
            100,
            0
        )
    # Create a filtered dataframe based on the selected filters.
    filtered_df = student_df.copy()

    if selected_course != "All":
        filtered_df = filtered_df[
            filtered_df["Course"] == selected_course
        ]

    if selected_risk != "All":
        filtered_df = filtered_df[
            filtered_df["Risk Level"] == selected_risk
        ]

    filtered_df = filtered_df[
        filtered_df["Attendance"] >= minimum_attendance
    ]
    
    if filtered_df.empty:
        st.warning("No students match the selected filters. Please adjust the filters.")
    
    # Calculate metrics based on the filtered dataframe.
    st.subheader("Filtered Dashboard Metrics")

    filtered_total_students = len(filtered_df)

    if filtered_total_students > 0:
        filtered_average_score = filtered_df["Score"].mean()
        filtered_average_attendance = filtered_df["Attendance"].mean()
        filtered_high_risk_students = filtered_df[
            filtered_df["Risk Level"] == "High Risk"
        ].shape[0]
    else:
        filtered_average_score = 0
        filtered_average_attendance = 0
        filtered_high_risk_students = 0
    
    # Display filter metric card
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("Students", filtered_total_students)

    with metric_col2:
        st.metric("Average Score", round(filtered_average_score, 2))

    with metric_col3:
        st.metric(
            "Average Attendance",
            f"{round(filtered_average_attendance, 2)}%"
        )

    with metric_col4:
        st.metric("High Risk", filtered_high_risk_students)
    
    # Add course Summary table
    st.subheader("Course Summary")

    if filtered_total_students > 0:
        course_summary = filtered_df.groupby("Course").agg(
            Students=("Student Name", "count"),
            Average_Score=("Score", "mean"),
            Average_Attendance=("Attendance", "mean"),
            Average_Study_Hours=("Study Hours", "mean")
        ).reset_index()

        st.dataframe(course_summary)
    else:
        st.info("No course summary available for the selected filters.")
    
    # Add Risk Level Summary Table
    st.subheader("Risk Level Summary")

    if filtered_total_students > 0:
        risk_summary = filtered_df["Risk Level"].value_counts().reset_index()
        risk_summary.columns = ["Risk Level", "Students"]

        st.dataframe(risk_summary)
    else:
        st.info("No risk summary available for the selected filters.")
    
    # Add streamlit chart session
    st.subheader("Streamlit Charts")

    chart_col1, chart_col2 = st.columns(2)

    # Add students score chart
    with chart_col1:
        st.write("Student Scores")

        if filtered_total_students > 0:
            score_chart = filtered_df.set_index("Student Name")["Score"]
            st.bar_chart(score_chart)
        else:
            st.info("No score chart available.")
    
    # Add course count chart
    with chart_col2:
        st.write("Students by Course")

        if filtered_total_students > 0:
            course_count = filtered_df["Course"].value_counts()
            st.bar_chart(course_count)
        else:
            st.info("No course count chart available.")
    
    # Add plotly charts session
    st.subheader("Interactive Plotly Charts")

    plotly_col1, plotly_col2 = st.columns(2)

    # Add Plotly Risk Distribution Chart
    with plotly_col1:
        st.write("Risk Level Distribution")

        if filtered_total_students > 0:
            risk_summary_chart = filtered_df["Risk Level"].value_counts().reset_index()
            risk_summary_chart.columns = ["Risk Level", "Students"]

            fig_risk = px.bar(
                risk_summary_chart,
                x="Risk Level",
                y="Students",
                color="Risk Level",
                title="Risk Level Distribution",
                color_discrete_map={
                    "Low Risk": "#16A34A",
                    "Medium Risk": "#F59E0B",
                    "High Risk": "#DC2626"
                }
            )

            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info("No risk distribution chart available.")
    
    # Add Plotly Score by Student Chart
    with plotly_col2:
        st.write("Student Scores by Risk Level")

        if filtered_total_students > 0:
            fig_score = px.bar(
                filtered_df,
                x="Student Name",
                y="Score",
                color="Risk Level",
                title="Student Scores by Risk Level",
                color_discrete_map={
                    "Low Risk": "#16A34A",
                    "Medium Risk": "#F59E0B",
                    "High Risk": "#DC2626"
                }
            )

            st.plotly_chart(fig_score, use_container_width=True)
        else:
            st.info("No score chart available.")
    
    # Add Filtered Student Records Table
    st.subheader("Filtered Student Records")

    if filtered_total_students > 0:
        st.dataframe(filtered_df)
    else:
        st.info("No student records to display.")

    # Add Ethical Visualization Reminder
    st.warning(
        "Ethics Reminder: Visualizations should support students and guide "
        "academic support decisions, not label or punish students."
    )

    total_students = len(student_df)
    average_score = student_df["Score"].mean()
    average_attendance = student_df["Attendance"].mean()
    high_risk_students = student_df[
        student_df["Risk Level"] == "High Risk"
    ].shape[0]

    # Dashboard Matrics
    st.subheader("Dashboard Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Students", total_students)

    with col2:
        st.metric("Average Score", round(average_score, 2))

    with col3:
        st.metric("Average Attendance", f"{round(average_attendance, 2)}%")

    with col4:
        st.metric("High Risk", high_risk_students)

    st.subheader("Student Records")
    st.write("This table shows student data loaded from students.csv.")
    st.dataframe(student_df)

    st.subheader("Charts")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("Student Score Chart")
        score_chart = student_df.set_index("Student Name")["Score"]
        st.bar_chart(score_chart)

    with chart_col2:
        st.write("Course Count")
        course_count = student_df["Course"].value_counts()
        st.bar_chart(course_count)

    st.info(
        "Ethics Reminder: Academic monitoring should support students, "
        "not label or punish them."
    )

#Update the Student Data page to show the full dataset with risk levels.
elif selected_page == "Student Data":
    st.title("Student Data")

    st.write(
        "This page displays and inspects the dataset loaded from students.csv."
    )

    st.subheader("Data Inspection")

    st.write("Rows and Columns:", student_df.shape)

    st.write("Column Names:")
    st.write(student_df.columns.tolist())

    st.write("First 5 Rows:")
    st.dataframe(student_df.head())

    st.subheader("Full Student Dataset")
    st.dataframe(student_df)

#Create a page where users can enter one student's score and attendance to check risk level.
elif selected_page == "Risk Checker":
    st.title("Single Student Risk Checker")

    st.write(
        "Enter student information to check risk level. "
        "The result is based on score and attendance."
    )

    st.info(
        "This tool is for academic support. Risk results should help students, "
        "not label or punish them."
    )

    with st.form("risk_checker_form"):
        input_name = st.text_input("Student Name")
        input_score = st.number_input("Score", 0, 100, 50)
        input_attendance = st.number_input("Attendance", 0, 100, 50)
        submitted = st.form_submit_button("Check Risk")
    
    # Add Risk Calculation After Validation
    if submitted:
        if input_name.strip() == "":
            st.warning("Please enter the student name.")
        else:
            risk_result = get_risk_level(
                input_score,
                input_attendance
            )

            result = {
                "Student Name": input_name.strip(),
                "Score": input_score,
                "Attendance": input_attendance,
                "Risk Level": risk_result
            }

            st.session_state["risk_history"].append(result)

            if risk_result == "Low Risk":
                st.success("Risk Level: Low Risk")
                st.write("Student appears on track.")
            elif risk_result == "Medium Risk":
                st.warning("Risk Level: Medium Risk")
                st.write("Monitor progress and provide guidance.")
            else:
                st.error("Risk Level: High Risk")
                st.write("Student may need additional support.")

            st.write("Student Name:", input_name.strip())
            st.write("Score:", input_score)
            st.write("Attendance:", input_attendance)
    
    # Add Recent Risk Checks Section
    st.subheader("Recent Risk Checks")
 
    # Display Risk History Table
    if len(st.session_state["risk_history"]) > 0:
        history_df = pd.DataFrame(
            st.session_state["risk_history"]
        )

        st.dataframe(history_df)

        if st.button("Clear History"):
            st.session_state["risk_history"] = []
            st.success("Risk check history cleared.")
    else:
        st.info("No risk checks yet.")

    st.warning(
        "Ethics Reminder: Risk results should be used as guidance for support, "
        "not as final judgment about a student."
    )

#Update the About page with Lab 02 information and an ethics reminder.

else:
    st.title("About")

    st.write("This app is part of Lab 05.")
    st.write("Course: Web App Development for Data Science")
    st.write("Project Theme: EduRisk Analytics")
    st.write("Topic: Visualization and Interactivity")

    st.info(
        "This version improves the Dashboard page using grouped summaries, "
        "interactive filters, Streamlit charts, and Plotly charts."
    )

    st.warning(
        "Ethics Reminder: Student performance visualizations should be used "
        "responsibly to support learning and student success."
    )