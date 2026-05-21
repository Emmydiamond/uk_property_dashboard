import joblib
import streamlit as st
import pandas as pd
import plotly.express as px


with open("style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ======================
# PAGE SETTINGS
# ======================

st.set_page_config(
    page_title="UK Property Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ======================
# LOAD DATA
# ======================

df = pd.read_csv("uk_dashboard_data.csv")

# ======================
# LOAD MODEL
# ======================

try:
    model = joblib.load("model/random_forest.pkl")
    encoders = joblib.load("model/encoders.pkl")
    model_loaded = True

except:
    model_loaded = False
# ======================
# SIDEBAR FILTERS
# ======================

st.sidebar.header("Filters")

# Clean filter values

years = [x for x in sorted(df["year"].dropna().unique())]
property_types = [x for x in sorted(df["property_type"].dropna().unique())]
tenure_types = [x for x in sorted(df["tenure_type"].dropna().unique())]

year = st.sidebar.multiselect(
    "Select Year",
    options=years,
    default=years
)

property_type = st.sidebar.multiselect(
    "Property Type",
    options=property_types,
    default=property_types
)

tenure = st.sidebar.multiselect(
    "Tenure Type",
    options=tenure_types,
    default=tenure_types
)

# Apply filters

filtered_df = df[
    (df["year"].isin(year)) &
    (df["property_type"].isin(property_type)) &
    (df["tenure_type"].isin(tenure))
]
# ======================
# TITLE
# ======================

st.image(
    "assets/logo.png",
    width=120
)

st.title("UK Property Price Analytics Dashboard")

st.markdown("---")

# ======================
# KPI CARDS
# ======================

avg_price = filtered_df["Price"].mean()
transactions = filtered_df.shape[0]
max_price = filtered_df["Price"].max()

col1,col2,col3 = st.columns(3)

col1.metric(
    "Average Price",
    f"£{avg_price:,.0f}"
)

col2.metric(
    "Total Transactions",
    f"{transactions:,}"
)

col3.metric(
    "Highest Price",
    f"£{max_price:,.0f}"
)

st.markdown("---")

# ======================
# MARKET SUMMARY
# ======================

st.markdown("---")
st.subheader("Market Summary")

col1, col2, col3 = st.columns(3)

most_common = (
    filtered_df["property_type"]
    .mode()[0]
)

highest_district = (
    filtered_df.groupby("District")["Price"]
    .mean()
    .idxmax()
)

new_build_percent = (
    (filtered_df["new_build_status"]=="New")
    .mean()*100
)

col1.info(
    f"Most common property:\n\n{most_common}"
)

col2.info(
    f"Highest-value district:\n\n{highest_district}"
)

col3.info(
    f"New builds:\n\n{new_build_percent:.1f}%"
)

# Download filtered data

st.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="uk_property_filtered.csv",
    mime="text/csv"
)
# ======================
# MARKET OVERVIEW
# ======================

st.subheader("Market Overview")

col1,col2 = st.columns(2)

# Average price trend

price_trend = (
    filtered_df
    .groupby("year")["Price"]
    .mean()
    .reset_index()
)

fig1 = px.line(
    price_trend,
    x="year",
    y="Price",
    markers=True,
    title="Average Property Price Over Time",
    color_discrete_sequence=["#1f3c88"]
)
col1.plotly_chart(
    fig1,
    use_container_width=True
)

# Transaction trend

transaction_count = (
    filtered_df
    .groupby("year")
    .size()
    .reset_index(name="Transactions")
)
fig2 = px.bar(
    transaction_count,
    x="year",
    y="Transactions",
    title="Transactions Per Year",
    color_discrete_sequence=["#4a69bd"]
)

col2.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("---")

# ======================
# PRICE DRIVERS
# ======================

st.markdown("---")
st.subheader("Price Drivers")

col1, col2 = st.columns(2)

# Price by Property Type

# Average price by property type

property_avg = (
    filtered_df
    .groupby("property_type")["Price"]
    .mean()
    .reset_index()
)

fig3 = px.bar(
    property_avg,
    x="property_type",
    y="Price",
    text="Price",
    title="Average Property Price by Property Type",
    color="Price",
    color_continuous_scale="Blues"
)

fig3.update_traces(
    texttemplate='£%{text:,.0f}',
    textposition='outside'
)

fig3.update_layout(
    yaxis_title="Average Price (£)"
)

col1.plotly_chart(
    fig3,
    use_container_width=True
)
# Average price by tenure

tenure_price = (
    filtered_df
    .groupby("tenure_type")["Price"]
    .mean()
    .reset_index()
)

fig4 = px.bar(
    tenure_price,
    x="tenure_type",
    y="Price",
    title="Average Price by Tenure Type",
    color="tenure_type"
)

col2.plotly_chart(
    fig4,
    use_container_width=True
)

# New vs Existing comparison

newbuild_price = (
    filtered_df
    .groupby("new_build_status")["Price"]
    .mean()
    .reset_index()
)

fig5 = px.bar(
    newbuild_price,
    x="new_build_status",
    y="Price",
    title="New vs Existing Property Prices",
    color="new_build_status"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)
# ======================
# LOCATION ANALYSIS
# ======================

st.markdown("---")
st.subheader("Location Analysis")

col1, col2 = st.columns(2)

# Top 10 districts by average price

top_districts = (
    filtered_df
    .groupby("District")["Price"]
    .mean()
    .reset_index()
    .sort_values(
        by="Price",
        ascending=False
    )
    .head(10)
)

# Horizontal chart

fig6 = px.bar(
    top_districts,
    y="District",
    x="Price",
    orientation="h",
    title="Top 10 Districts by Average Price",
color_continuous_scale="Blues"
)

fig6.update_layout(
    yaxis={'categoryorder':'total ascending'}
)

col1.plotly_chart(
    fig6,
    use_container_width=True
)

# Top district trends

district_trend = (
    filtered_df
    .groupby(
        ["year","District"]
    )["Price"]
    .mean()
    .reset_index()
)

top5 = (
    filtered_df
    .groupby("District")["Price"]
    .mean()
    .nlargest(5)
    .index
)

district_trend = district_trend[
    district_trend["District"].isin(top5)
]

fig7 = px.line(
    district_trend,
    x="year",
    y="Price",
    color="District",
    markers=True,
    title="Property Price Trends by Top Districts"
)

col2.plotly_chart(
    fig7,
    use_container_width=True
)

# ======================
# ML PROPERTY PREDICTION
# ======================

st.markdown("---")

st.subheader("ML Property Price Prediction")
col1, col2 = st.columns(2)

with col1:

    selected_property = st.selectbox(
        "Property Type",
        sorted(df["property_type"].dropna().astype(str).unique())
    )

    selected_tenure = st.selectbox(
        "Tenure Type",
        sorted(df["tenure_type"].dropna().astype(str).unique())
    )

with col2:

    selected_district = st.selectbox(
        "District",
        sorted(df["District"].dropna().astype(str).unique())
    )

    selected_build = st.selectbox(
        "Build Status",
        sorted(df["new_build_status"].dropna().astype(str).unique())
    )

selected_year = st.slider(
    "Year",
    int(df["year"].min()),
    int(df["year"].max()),
    int(df["year"].max())
)

selected_month = st.slider(
    "Month",
    1,
    12,
    1
)

predict_now = st.button(
    "Predict Property Price"
)

input_data = pd.DataFrame({

    "property_type":[selected_property],
    "new_build_status":[selected_build],
    "tenure_type":[selected_tenure],
    "District":[selected_district],
    "year":[selected_year],
    "month_num":[selected_month]

})

# Encode text variables

# ======================
# ENCODE INPUT DATA
# ======================

categorical_cols = [
    "property_type",
    "new_build_status",
    "tenure_type",
    "District"
]

if model_loaded:

    for col in input_data.columns:

        if col in categorical_cols:

            input_data[col] = (
                encoders[col]
                .transform(input_data[col])
            )

# Force numeric format

input_data["year"] = pd.to_numeric(
    input_data["year"]
)

input_data["month_num"] = pd.to_numeric(
    input_data["month_num"]
)

# Ensure exact column order used during training

input_data = input_data[[
    "property_type",
    "new_build_status",
    "tenure_type",
    "District",
    "year",
    "month_num"
]]

 if predict_now:

    prediction = model.predict(input_data)[0]

    st.metric(
        "Predicted Property Price",
        f"£{prediction:,.0f}"
    )

    else:

        st.warning(
            "ML model temporarily unavailable in cloud deployment."
        )
