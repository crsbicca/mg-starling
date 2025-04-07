import streamlit as st
import pandas as pd
import plotly.express as px

years = ["2024", "2025-26", "2026-27", "2027-28", "2028-29"]

st.set_page_config(page_title="Starling Media Spend Impact Tool", layout="wide")
st.title("Starling Media Spend Impact Tool")

st.sidebar.header("Inputs")

base_spend = st.sidebar.number_input("Base Media Spend:", min_value=1_000_000, value=32_000_000)
budget_upweight = st.sidebar.slider("Budget Upweight (%)", min_value=0, max_value=100, value=10)
effectiveness = st.sidebar.slider("Effectiveness Multiplier", min_value=0.1, max_value=5.0, value=2.2, step=0.1)
natural_growth = st.sidebar.slider("Natural Growth (%)", min_value=0, max_value=20, value=5)
split = st.sidebar.selectbox("Brand/Performance Split:", ["50/50", "60/40", "70/30", "80/20"])
brand_effectiveness = st.sidebar.slider("Brand Effectiveness", min_value=0.0, max_value=1.0, value=0.6, step=0.1)
performance_effectiveness = st.sidebar.slider("Performance Effectiveness", min_value=0.0, max_value=1.0, value=0.4, step=0.1)

spend = [base_spend] * len(years)
upweight_value = [s * (budget_upweight / 100) for s in spend]
effectiveness_gain = [u * effectiveness for u in upweight_value]
natural_growth_val = [s * (natural_growth / 100) for s in spend]

brand_split = int(split.split("/")[0]) / 100
perf_split = 1 - brand_split

brand_effect = [e * brand_split * brand_effectiveness for e in effectiveness_gain]
perf_effect = [e * perf_split * performance_effectiveness for e in effectiveness_gain]

base_contribution = [s * 0.4 for s in spend]
media_contribution = [b + p for b, p in zip(brand_effect, perf_effect)]
total = [b + m + n for b, m, n in zip(base_contribution, media_contribution, natural_growth_val)]

cumulative_total = pd.Series(total).cumsum().tolist()

df = pd.DataFrame({
    "Year": years,
    "Spend": spend,
    "Upweight": upweight_value,
    "EffectivenessGain": effectiveness_gain,
    "NaturalGrowth": natural_growth_val,
    "BrandEffect": brand_effect,
    "PerformanceEffect": perf_effect,
    "BaseContribution": base_contribution,
    "MediaContribution": media_contribution,
    "Total": total,
    "CumulativeTotal": cumulative_total
})


#st.subheader("Cumulative Total Over Years")
fig = px.line(df, x="Year", y="CumulativeTotal", markers=True, title="Cumulative Impact Over Time")
fig.update_traces(line_color="#6935D3")  # Replace "blue" with your desired color
fig.update_layout(xaxis_title="Year", yaxis_title="Cumulative Total")
st.plotly_chart(fig)

st.subheader("Projection Table")
# Apply formatting only to numeric columns
numeric_columns = df.select_dtypes(include=['number']).columns
st.dataframe(df.style.format({col: "{:,.0f}" for col in numeric_columns}))

