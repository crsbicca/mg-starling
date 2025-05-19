import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
# Load the Excel file
df = pd.read_excel('starling.xlsx', engine='openpyxl')

# Streamlit app
st.set_page_config(page_title="BBC Performance Planner", layout="wide")
# Inject custom CSS to reduce padding above the title and change subtitle font size
st.markdown(
    """
    <style>
    .css-18e3th9 {
        padding-top: 0rem;
    }
    .css-1d391kg {
        padding-top: 0rem;
    }
    .css-1h6f3py {
        font-size: 14px;  /* Change this value to your desired font size */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('BBC Performance Planner')

# Sidebar for user inputs
st.sidebar.image('omni.png', width=200)  # Adjust the width as needed
st.sidebar.header('User Input Parameters')

# User input for Brand vs Performance allocation (default value 60% Brand Allocation)
brand_allocation = st.sidebar.slider('Owned Allocation (%)', 0, 100, 20)
performance_allocation = 100 - brand_allocation

# User input for Budget upweight
budget_upweight = st.sidebar.slider('Budget Upweight (%)', 0, 500, 155) / 100

# User input for Effectiveness
effectiveness = st.sidebar.slider('Frequency', 0, 20, 4) / 100


# Data
data = {
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"],
    "Reach": [4111111, 7400000, 9866667, 11511111, 12744444, 13566667, 13977778, 14388889, 14594444, 14800000]
}

# Create DataFrame
df = pd.DataFrame(data)

# Create Plotly Express line chart
fig = px.line(df, x="Month", y="Reach", markers=True)

# Add a vertical line to indicate the point of diminishing returns
fig.add_vline(x=6, line_dash="dash", line_color="red")

# Streamlit app
st.subheader('Cumulative Paid & Owned Reach')
st.plotly_chart(fig)
