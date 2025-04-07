import streamlit as st
import pandas as pd
import plotly.express as px

# Load the Excel file
df = pd.read_excel('starling.xlsx', engine='openpyxl')

# Streamlit app
st.set_page_config(page_title="Media Spend Impact Tool", layout="wide")
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

st.title('Media Spend Impact Tool')

# Sidebar for user inputs
st.sidebar.image('omni.png', width=200)  # Adjust the width as needed
st.sidebar.header('User Input Parameters')

# User input for Brand vs Performance allocation (default value 60% Brand Allocation)
brand_allocation = st.sidebar.slider('Brand Allocation (%)', 0, 100, 60)
performance_allocation = 100 - brand_allocation

# User input for Budget upweight
budget_upweight = st.sidebar.slider('Budget Upweight (%)', 0, 500, 128) / 100

# User input for Effectiveness
effectiveness = st.sidebar.slider('Effectiveness (%)', 0, 500, 220) / 100

# User input for Years (including 2024 as the first year)
years = st.sidebar.text_area('Years (comma-separated)', '2024,2025-26,2026-27,2027-28,2028-29')
years_list = [year.strip() for year in years.split(',')]

# Adjust the dataframe to match the number of years provided by the user
if len(years_list) > len(df):
    # Add new rows to the dataframe if there are more years provided than rows in the dataframe
    additional_rows = len(years_list) - len(df)
    df = pd.concat([df, pd.DataFrame(index=range(additional_rows))], ignore_index=True)
elif len(years_list) < len(df):
    # Remove rows from the dataframe if there are fewer years provided than rows in the dataframe
    df = df.iloc[:len(years_list)]

df['Year'] = years_list

# User input for Media Spend by year
media_spend_list = []
for year in years_list:
    media_spend = st.sidebar.number_input(f'Media Spend for {year}', value=32000000)
    media_spend_list.append(media_spend)

df['Media Spend'] = media_spend_list

# User input for Natural growth
natural_growth = st.sidebar.slider('Natural Growth (%)', 0, 500, 105) / 100

# User input for Base contribution (default value 40%)
base_contribution = st.sidebar.slider('Base Contribution (%)', 0, 100, 40) / 100

# User input for Media contribution (default value 30%)
media_contribution = st.sidebar.slider('Media Contribution (%)', 0, 100, 30) / 100

# User input for LT media contribution (default value 30%)
lt_media_contribution = st.sidebar.slider('LT Media Contribution (%)', 0, 100, 30) / 100

# Calculations based on user inputs and formulas in the sheet
df['Spend difference'] = df['Media Spend'].diff().fillna(0)

# Calculate Upweight (first year has default value of 600000)
upweight_list = [600000]
for i in range(1, len(df)):
    upweight_list.append(upweight_list[i-1] * budget_upweight)
df['Upweight'] = upweight_list

# Calculate Effectiveness Gain and Natural Growth (first year equals upweight of first year)
effectiveness_gain_list = [600000]
natural_growth_0_list = [600000]
for i in range(1, len(df)):
    effectiveness_gain_list.append(df['Upweight'].iloc[i] * effectiveness)
    natural_growth_0_list.append(effectiveness_gain_list[i] * natural_growth)
df['Effectiveness Gain'] = effectiveness_gain_list
df['Natural Growth'] = natural_growth_0_list

# Calculate Improvement
improvement_list = [0]
for i in range(1, len(df)):
    if i < 4:
        improvement_list.append(df['Natural Growth'].iloc[i] - df['Upweight'].iloc[0])
    else:
        improvement_list.append(df['Natural Growth'].iloc[i] - df['Upweight'].iloc[i-3])
df['Improvement'] = improvement_list

# Calculate Brand Effectiveness and Performance Effectiveness based on Improvement and Brand Allocation
df['Brand Effectiveness'] = df['Improvement'] * (brand_allocation / 100)
df['Performance Effectiveness'] = df['Improvement'] * (performance_allocation / 100)

# Calculate Base and Long term media impact based on new formulas
base_list = []
lt_media_impact_list = []
for i in range(len(df)):
    if i == 0:
        base_list.append((df['Upweight'].iloc[0] + df['Brand Effectiveness'].iloc[0]) * base_contribution)
        lt_media_impact_list.append((df['Upweight'].iloc[0] + df['Brand Effectiveness'].iloc[0]) * lt_media_contribution)
    else:
        base_list.append((df['Upweight'].iloc[0] + df['Brand Effectiveness'].iloc[i-1]) * base_contribution)
        lt_media_impact_list.append((df['Upweight'].iloc[0] + df['Brand Effectiveness'].iloc[i-1]) * lt_media_contribution)
df['Base'] = base_list
df['Long term media impact'] = lt_media_impact_list

# Calculate Media based on new formula
df['Media'] = (df['Upweight'].iloc[0] + (df['Performance Effectiveness'] * 2)) * media_contribution

# Calculate Totals and Cumulative Total based on new formulas
df['Totals'] = df[['Base', 'Media', 'Long term media impact']].sum(axis=1)
cumulative_total_list = [4300000]
for i in range(1, len(df)):
    cumulative_total_list.append(cumulative_total_list[i-1] + df['Totals'].iloc[i])
df['Cumulative Total'] = cumulative_total_list

# Order the table by Year DESC
df.sort_values(by='Year', ascending=False, inplace=True)

# Format all numbers to show comma thousand separator without decimal numbers
formatted_df = df[['Year', 'Media Spend', 'Upweight', 'Effectiveness Gain', 'Natural Growth', 'Improvement', 'Brand Effectiveness', 'Performance Effectiveness', 'Base', 'Media', 'Long term media impact', 'Totals', 'Cumulative Total']]
formatted_df.iloc[:,1:] = formatted_df.iloc[:,1:].applymap(lambda x: '{:,.0f}'.format(x))

# Main panel for chart and projection table
st.subheader('Cumulative Impact of Media Over Time')

# Sort the DataFrame by Year in ascending order
df = df.sort_values(by="Year")

fig = px.line(df, x="Year", y="Cumulative Total", markers=True)
fig.update_traces(line_color="#6935D3")  # Replace "blue" with your desired color
fig.update_layout(xaxis_title="Year", yaxis_title="Cumulative Total", height =350, width=1500)
st.plotly_chart(fig)


st.subheader('Projection Table')
st.dataframe(formatted_df, width=1500)