import streamlit as st
import pandas as pd

# Load the Excel file
df = pd.read_excel('starling.xlsx', engine='openpyxl')

# Streamlit app
st.title('Media Spend Projection')

# Sidebar for user inputs
st.sidebar.header('User Input Parameters')

# User input for Budget upweight
budget_upweight = st.sidebar.slider('Budget Upweight (%)', 0, 500, 128) / 100

# User input for Effectiveness
effectiveness = st.sidebar.slider('Effectiveness (%)', 0, 500, 220) / 100

# User input for Natural growth
natural_growth = st.sidebar.slider('Natural Growth (%)', 0, 500, 105) / 100

# User input for Base contribution
base_contribution = st.sidebar.slider('Base Contribution (%)', 0, 100, 50) / 100

# User input for Media contribution
media_contribution = st.sidebar.slider('Media Contribution (%)', 0, 100, 50) / 100

# User input for LT media contribution
lt_media_contribution = st.sidebar.slider('LT Media Contribution (%)', 0, 100, 50) / 100

# User input for Brand vs Performance allocation
brand_allocation = st.sidebar.slider('Brand Allocation (%)', 0, 100, 50)
performance_allocation = 100 - brand_allocation

# User input for Years
years = st.sidebar.text_area('Years (comma-separated)', '2025-26,2026-27,2027-28,2028-29')
years_list = [year.strip() for year in years.split(',')]

# Adjust the dataframe to match the number of years provided by the user
if len(years_list) > len(df):
    # Add new rows to the dataframe if there are more years provided than rows in the dataframe
    additional_rows = len(years_list) - len(df)
    df = pd.concat([df, pd.DataFrame(index=range(additional_rows))], ignore_index=True)
elif len(years_list) < len(df):
    # Remove rows from the dataframe if there are fewer years provided than rows in the dataframe
    df = df.iloc[:len(years_list)]

df['Year (ending march)'] = years_list

# User input for Media Spend by year
media_spend_list = []
for year in years_list:
    media_spend = st.sidebar.number_input(f'Media Spend for {year}', value=32000000)
    media_spend_list.append(media_spend)

df['Media Spend'] = media_spend_list

# Calculations based on user inputs and formulas in the sheet
df['Spend difference'] = df['Media Spend'].diff().fillna(0)

# Calculate Upweight
upweight_list = [600]
for i in range(1, len(df)):
    upweight_list.append(upweight_list[i-1] * budget_upweight)
df['Upweight'] = upweight_list

# Calculate Effectiveness Gain
df['Effectiveness Gain'] = df['Upweight'] * effectiveness

# Calculate Natural Growth_0
df['Natural Growth_0'] = df['Effectiveness Gain'] * natural_growth

# Calculate Improvement
improvement_list = [0]
for i in range(1, len(df)):
    if i < 4:
        improvement_list.append(df['Natural Growth_0'].iloc[i] - df['Upweight'].iloc[0])
    else:
        improvement_list.append(df['Natural Growth_0'].iloc[i] - df['Upweight'].iloc[i-3])
df['Improvement'] = improvement_list

df['Brand'] = brand_allocation / 100 * df['Media Spend']
df['Performance'] = performance_allocation / 100 * df['Media Spend']
df['Brand Effectiveness'] = df['Brand'] * df['Effectiveness Gain']
df['Performance Effectiveness'] = df['Performance'] * df['Effectiveness Gain']
df['Base'] = df['Media Spend'] * base_contribution
df['Media'] = df['Media Spend'] * media_contribution
df['Long term media impact'] = df['Media Spend'] * lt_media_contribution
df['Totals'] = df[['Base', 'Media', 'Long term media impact']].sum(axis=1)
df['Cumulative Total'] = df['Totals'].cumsum()

# Main panel for chart and projection table
st.subheader('Incremental Impact of Media Over Time')
st.line_chart(df[['Cumulative Total', 'Year (ending march)']].set_index('Year (ending march)'))

st.subheader('Projection Table')
st.dataframe(df[['Year (ending march)', 'Media Spend', 'Upweight', 'Effectiveness Gain', 'Natural Growth_0', 'Improvement', 'Brand Effectiveness', 'Performance Effectiveness', 'Base', 'Media', 'Long term media impact', 'Totals', 'Cumulative Total']])