"""
Regional Revenue-Manager Dashboard & OLAP Analytics Web Application
Project: An OLAP-Based Revenue Analytics Pipeline for Hotel-Chain Revenue Data Mining
Author: BUDUPULA VIVEKA
Mentor: Ms. G. Hema Sri
Domain: Big Data Analytics, Data Warehousing & Visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import project modules
from etl_pipeline import generate_raw_booking_exports, build_star_schema
from olap_engine import HotelRevenueOLAPCube
from data_mining import HotelDataMiningEngine

# Streamlit Page Configuration
st.set_page_config(
    page_title="Hotel-Chain Revenue OLAP Analytics Pipeline",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for modern executive dashboard feel
st.markdown("""
<style>
    .main-header {
        font-size: 1.85rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .kpi-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .kpi-title {
        font-size: 0.82rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0F172A;
    }
    .meta-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #EEF2FF;
        color: #4338CA;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Running ETL Pipeline & Building Star Schema...")
def load_and_initialize_pipeline():
    """Generates synthetic PMS booking records and builds the dimensional star schema warehouse."""
    raw_df = generate_raw_booking_exports(n_records=8500, seed=42)
    schema = build_star_schema(raw_df)
    return schema


# Load Star Schema Data
star_schema = load_and_initialize_pipeline()
cube_engine = HotelRevenueOLAPCube(star_schema)
full_cube = cube_engine.get_cube()


# -------------------------------------------------------------
# SIDEBAR CONTROLS (OLAP Slicers)
# -------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/hotel-star.png", width=64)
st.sidebar.title("OLAP Slicers & Filters")
st.sidebar.caption("Multi-dimensional controls for revenue managers")

# Region Filter (OLAP Slice)
available_regions = ["All Regions"] + sorted(list(full_cube["region"].unique()))
selected_region = st.sidebar.selectbox("Region (Geographic Slice):", available_regions)

# Property Filter (dynamically filtered by region)
if selected_region != "All Regions":
    prop_candidates = sorted(list(full_cube[full_cube["region"] == selected_region]["property_name"].unique()))
else:
    prop_candidates = sorted(list(full_cube["property_name"].unique()))

selected_properties = st.sidebar.multiselect(
    "Properties:",
    options=prop_candidates,
    default=prop_candidates
)

# Quarter / Season Filter
available_quarters = sorted(list(full_cube["quarter"].dropna().unique()))
selected_quarters = st.sidebar.multiselect(
    "Quarters:",
    options=available_quarters,
    default=available_quarters
)

# Room Type Filter
available_rooms = sorted(list(full_cube["room_type"].unique()))
selected_rooms = st.sidebar.multiselect(
    "Room Categories:",
    options=available_rooms,
    default=available_rooms
)

# Apply OLAP Filters to Cube
filtered_cube = full_cube.copy()
if selected_region != "All Regions":
    filtered_cube = filtered_cube[filtered_cube["region"] == selected_region]

if selected_properties:
    filtered_cube = filtered_cube[filtered_cube["property_name"].isin(selected_properties)]

if selected_quarters:
    filtered_cube = filtered_cube[filtered_cube["quarter"].isin(selected_quarters)]

if selected_rooms:
    filtered_cube = filtered_cube[filtered_cube["room_type"].isin(selected_rooms)]

# Ensure data is not empty
if filtered_cube.empty:
    st.warning("⚠️ No data available for the selected filter combination. Resetting to full dataset.")
    filtered_cube = full_cube.copy()

# Sidebar Project Meta Details
st.sidebar.markdown("---")
st.sidebar.subheader("Project Information")
st.sidebar.markdown("**Candidate:** BUDUPULA VIVEKA")
st.sidebar.markdown("**Guide:** Ms. G. Hema Sri")
st.sidebar.markdown("**Domain:** Big Data Analytics, Data Warehousing & Visualization")
st.sidebar.markdown("**Architecture:** Star Schema + Multidimensional OLAP Cube")


# -------------------------------------------------------------
# MAIN APP HEADER
# -------------------------------------------------------------
st.markdown('<div class="main-header">🏨 Hotel-Chain Revenue OLAP Analytics & Data Mining Pipeline</div>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-header">
    <span class="meta-badge">Candidate: BUDUPULA VIVEKA</span>
    <span class="meta-badge">Guide: Ms. G. Hema Sri</span>
    <span class="meta-badge">Domain: Big Data Analytics & Data Warehousing</span>
</div>
""", unsafe_allow_html=True)

# Compute Current Global KPIs
kpis = cube_engine.calculate_chain_kpis(filtered_cube)

kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
with kpi_c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Room Revenue</div>
        <div class="kpi-value">₹ {kpis['total_revenue']:,.0f}</div>
        <small style="color: #10B981;">▲ Across Sliced Dimensions</small>
    </div>
    """, unsafe_allow_html=True)

with kpi_c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Average Daily Rate (ADR)</div>
        <div class="kpi-value">₹ {kpis['chain_adr']:,.2f}</div>
        <small style="color: #64748B;">Total Revenue / Rooms Sold</small>
    </div>
    """, unsafe_allow_html=True)

with kpi_c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Average Occupancy Rate</div>
        <div class="kpi-value">{kpis['chain_occupancy_pct']:.1f}%</div>
        <small style="color: #64748B;">Rooms Sold / Total Capacity</small>
    </div>
    """, unsafe_allow_html=True)

with kpi_c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">RevPAR (Yield Performance)</div>
        <div class="kpi-value">₹ {kpis['chain_revpar']:,.2f}</div>
        <small style="color: #2563EB;">ADR × Occupancy Rate</small>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# -------------------------------------------------------------
# NAVIGATION TABS
# -------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Regional Executive Overview",
    "🧊 OLAP Multidimensional Cube",
    "🏢 Multi-Property Benchmarking",
    "🤖 Data Mining & Predictive ML",
    "🏛️ Data Warehouse & Star Schema",
    "📈 What-If Pricing Simulator"
])


# =============================================================
# TAB 1: REGIONAL EXECUTIVE OVERVIEW
# =============================================================
with tab1:
    st.subheader("Regional Performance & Yield Analytics")
    st.markdown("Compare revenue generation, occupancy levels, and RevPAR performance across hotel properties.")

    col1, col2 = st.columns([3, 2])

    with col1:
        # Property-level RevPAR & Occupancy Comparison
        prop_summary = cube_engine.roll_up(
            group_by_dims=["property_name", "region", "tier"],
            sub_cube=filtered_cube
        ).sort_values(by="avg_revpar", ascending=False)

        fig_bar = px.bar(
            prop_summary,
            x="property_name",
            y="avg_revpar",
            color="region",
            text="avg_revpar",
            title="Property RevPAR Comparison (₹) by Region",
            labels={"avg_revpar": "Average RevPAR (₹)", "property_name": "Property Name"},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bar.update_traces(texttemplate='₹%{text:.0f}', textposition='outside')
        fig_bar.update_layout(xaxis_tickangle=-25, template="plotly_white", height=420)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Regional Revenue Distribution
        region_summary = cube_engine.roll_up(
            group_by_dims=["region"],
            sub_cube=filtered_cube
        )
        fig_pie = px.pie(
            region_summary,
            names="region",
            values="total_revenue",
            title="Regional Revenue Contribution",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_pie.update_traces(textinfo="label+percent")
        fig_pie.update_layout(height=420, template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Monthly Trends (Time Dimension Roll-up)
    st.markdown("#### Monthly RevPAR and Occupancy Rate Trajectory")
    month_summary = cube_engine.roll_up(
        group_by_dims=["month_num", "month"],
        sub_cube=filtered_cube
    ).sort_values("month_num")

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=month_summary["month"],
        y=month_summary["avg_revpar"],
        name="RevPAR (₹)",
        mode="lines+markers",
        line=dict(color="#2563EB", width=3)
    ))
    fig_trend.add_trace(go.Bar(
        x=month_summary["month"],
        y=month_summary["avg_occupancy_pct"],
        name="Occupancy Rate (%)",
        yaxis="y2",
        opacity=0.35,
        marker=dict(color="#10B981")
    ))

    fig_trend.update_layout(
        title="12-Month Performance Dynamics: RevPAR vs. Occupancy %",
        xaxis=dict(title="Month"),
        yaxis=dict(title="RevPAR (₹)", side="left"),
        yaxis2=dict(title="Occupancy Rate (%)", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=380
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# =============================================================
# TAB 2: OLAP MULTIDIMENSIONAL CUBE
# =============================================================
with tab2:
    st.subheader("Multidimensional OLAP Operations Engine")
    st.markdown("Perform interactive **Roll-up**, **Drill-down**, **Slicing**, **Dicing**, and **Pivot Matrix** analysis.")

    olap_mode = st.radio(
        "Select OLAP Operation to Execute:",
        ["1. Dynamic Pivot Matrix (Cross-Tabulation)", "2. Roll-up Aggregation", "3. Drill-down Hierarchy"],
        horizontal=True
    )

    if "1. Dynamic Pivot Matrix" in olap_mode:
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            row_dim = st.selectbox("Row Dimension (Axis 0):", ["property_name", "region", "room_type", "tier"], index=0)
        with pc2:
            col_dim = st.selectbox("Column Dimension (Axis 1):", ["quarter", "month", "season", "day_of_week"], index=0)
        with pc3:
            metric_choice = st.selectbox("Aggregation Metric:", ["avg_revpar", "avg_adr", "avg_occupancy_pct", "total_revenue"], index=0)

        pivot_df = cube_engine.pivot_cube(
            index_dim=row_dim,
            column_dim=col_dim,
            metric=metric_choice,
            sub_cube=filtered_cube
        )

        st.markdown(f"#### OLAP Pivot Matrix: `{row_dim}` vs. `{col_dim}` (Metric: `{metric_choice}`)")
        st.dataframe(pivot_df.style.background_gradient(cmap="Blues"), use_container_width=True)

        # Plotly Heatmap visualization of the Pivot Table
        fig_heat = px.imshow(
            pivot_df,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis",
            title=f"Heatmap Visualization: {metric_choice} by {row_dim} and {col_dim}"
        )
        fig_heat.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

    elif "2. Roll-up Aggregation" in olap_mode:
        st.markdown("Roll-up aggregates granular booking entries up to higher level enterprise dimensions.")
        hierarchy_level = st.selectbox(
            "Select Roll-up Hierarchy Level:",
            [
                ["region"],
                ["region", "city"],
                ["quarter", "region"],
                ["season", "room_type"]
            ]
        )
        rolled = cube_engine.roll_up(group_by_dims=hierarchy_level, sub_cube=filtered_cube)
        st.dataframe(rolled, use_container_width=True)

    elif "3. Drill-down Hierarchy" in olap_mode:
        st.markdown("Drill-down navigates from regional high-level summaries into property-level and room-type granularity.")
        dd_region = st.selectbox("Choose Parent Region to Drill Into:", sorted(list(full_cube["region"].unique())))
        drilled = cube_engine.drill_down(
            parent_dim="region",
            child_dim="property_name",
            parent_value=dd_region
        )
        st.markdown(f"#### Granular Breakdown for Region: **{dd_region}**")
        st.dataframe(drilled, use_container_width=True)

        fig_drill = px.bar(
            drilled,
            x="property_name",
            y="avg_revpar",
            color="avg_occupancy_pct",
            text="avg_revpar",
            title=f"Properties in {dd_region} - RevPAR & Occupancy Intensity",
            color_continuous_scale="Tealgrn"
        )
        st.plotly_chart(fig_drill, use_container_width=True)


# =============================================================
# TAB 3: MULTI-PROPERTY BENCHMARKING
# =============================================================
with tab3:
    st.subheader("Multi-Property Head-to-Head Benchmarking")
    st.markdown("Compare properties on key hospitality indicators to identify underperforming or leading assets.")

    all_props = sorted(list(full_cube["property_name"].unique()))
    benchmark_props = st.multiselect(
        "Select Properties to Benchmark:",
        options=all_props,
        default=all_props[:3] if len(all_props) >= 3 else all_props
    )

    if benchmark_props:
        bm_cube = full_cube[full_cube["property_name"].isin(benchmark_props)]
        bm_summary = cube_engine.roll_up(
            group_by_dims=["property_name", "region", "tier"],
            sub_cube=bm_cube
        )

        st.markdown("#### Comparative Metric Summary")
        st.dataframe(
            bm_summary[[
                "property_name", "region", "tier", "total_revenue", "avg_adr", "avg_occupancy_pct", "avg_revpar"
            ]].rename(columns={
                "property_name": "Property",
                "region": "Region",
                "tier": "Star Tier",
                "total_revenue": "Total Revenue (₹)",
                "avg_adr": "ADR (₹)",
                "avg_occupancy_pct": "Occupancy (%)",
                "avg_revpar": "RevPAR (₹)"
            }),
            use_container_width=True
        )

        # Bubble chart: ADR vs Occupancy with RevPAR as bubble size
        fig_bubble = px.scatter(
            bm_summary,
            x="avg_adr",
            y="avg_occupancy_pct",
            size="total_revenue",
            color="property_name",
            text="property_name",
            labels={"avg_adr": "Average Daily Rate (₹)", "avg_occupancy_pct": "Occupancy Rate (%)"},
            title="Strategic Positioning Matrix: ADR vs. Occupancy Rate (Bubble size = Total Revenue)"
        )
        fig_bubble.update_traces(textposition="top center")
        fig_bubble.update_layout(template="plotly_white", height=450)
        st.plotly_chart(fig_bubble, use_container_width=True)


# =============================================================
# TAB 4: DATA MINING & PREDICTIVE ML
# =============================================================
with tab4:
    st.subheader("Data Mining & Predictive Analytics")
    st.markdown("Machine learning models applied on booking logs for revenue optimization and risk mitigation.")

    # Initialize data mining engine
    mining_engine = HotelDataMiningEngine(star_schema["raw_dataset"])

    ml_sub_tab1, ml_sub_tab2, ml_sub_tab3 = st.tabs([
        "🛡️ Booking Cancellation Classifier",
        "📈 30-Day RevPAR Forecaster",
        "👥 Customer Segmentation (K-Means)"
    ])

    with ml_sub_tab1:
        st.markdown("#### Supervised Learning: Cancellation Risk Prediction")
        st.markdown("Trained using **Random Forest Classifier** to flag potential booking cancellations before arrival.")

        with st.spinner("Training classification pipeline..."):
            metrics = mining_engine.train_cancellation_model()

        # Display Metrics
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Model Accuracy", f"{metrics['accuracy']*100:.1f}%")
        m2.metric("Precision", f"{metrics['precision']*100:.1f}%")
        m3.metric("Recall", f"{metrics['recall']*100:.1f}%")
        m4.metric("F1-Score", f"{metrics['f1']*100:.1f}%")
        m5.metric("ROC-AUC Score", f"{metrics['roc_auc']:.3f}")

        st.markdown("---")
        st.markdown("##### 🔍 Test Real-Time Cancellation Propensity for a New Booking")

        input_c1, input_c2, input_c3 = st.columns(3)
        with input_c1:
            inp_lead = st.slider("Lead Time (Days before check-in):", min_value=0, max_value=120, value=25)
            inp_nights = st.number_input("Nights of Stay:", min_value=1, max_value=30, value=2)
            inp_guests = st.number_input("Number of Guests:", min_value=1, max_value=6, value=2)

        with input_c2:
            inp_adr = st.number_input("Booking ADR (₹):", min_value=1500, max_value=40000, value=6500)
            inp_region = st.selectbox("Hotel Region:", ["South", "West", "North"])
            inp_tier = st.selectbox("Hotel Tier:", ["5-Star", "4-Star"])

        with input_c3:
            inp_room = st.selectbox("Room Category:", ["Standard Room", "Deluxe Room", "Executive Suite", "Presidential Suite"])
            inp_channel = st.selectbox("Booking Channel:", [
                "Direct Website", "OTA (Booking.com)", "OTA (MakeMyTrip / Expedia)", "Corporate Contract", "Walk-In / Direct Call"
            ])
            inp_segment = st.selectbox("Customer Segment:", ["Business", "Leisure", "Family Vacation", "Conference / Group"])

        if st.button("Evaluate Booking Cancellation Propensity", type="primary"):
            pred_res = mining_engine.predict_single_booking({
                "lead_time": inp_lead,
                "nights": inp_nights,
                "num_guests": inp_guests,
                "adr": inp_adr,
                "region": inp_region,
                "tier": inp_tier,
                "room_type": inp_room,
                "channel_name": inp_channel,
                "customer_segment": inp_segment
            })

            prob = pred_res["cancellation_probability"]
            risk = pred_res["risk_level"]
            color = "#EF4444" if risk == "High Risk" else "#F59E0B" if risk == "Moderate Risk" else "#10B981"

            st.markdown(f"""
            <div style="background-color: #F8FAFC; padding: 20px; border-radius: 8px; border-left: 6px solid {color}; margin-top: 15px;">
                <h4 style="margin: 0; color: {color};">{risk} (Cancellation Probability: {prob}%)</h4>
                <p style="margin: 5px 0 0 0; color: #4B5563;">
                    Predicted Action: {'Booking likely to be cancelled. Suggest requiring non-refundable deposit or overbooking safety buffer.' if pred_res['predicted_cancellation'] == 1 else 'Booking likely to materialize. Standard confirmation workflow.'}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### Feature Importance in Predicting Cancellations")
        feat_df = mining_engine.feature_importance_df.head(8)
        fig_feat = px.bar(
            feat_df,
            x="importance",
            y="feature",
            orientation="h",
            title="Top Factors Influencing Booking Cancellations",
            color="importance",
            color_continuous_scale="Reds"
        )
        fig_feat.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white", height=320)
        st.plotly_chart(fig_feat, use_container_width=True)

    with ml_sub_tab2:
        st.markdown("#### Time-Series RevPAR Demand Forecasting")
        st.markdown("Decomposes trend and day-of-week seasonality to generate a 30-day forward projection.")

        forecast_df = mining_engine.forecast_revpar(filtered_cube, days_ahead=30)

        fig_fore = go.Figure()
        # Historical last 45 days
        hist_recent = filtered_cube.groupby("date").agg(
            revenue=("room_revenue", "sum"),
            cap=("allocated_rooms", "sum")
        ).reset_index()
        hist_recent["revpar"] = (hist_recent["revenue"] / hist_recent["cap"]).round(2)
        hist_recent["date"] = pd.to_datetime(hist_recent["date"])
        hist_recent = hist_recent.sort_values("date").tail(45)

        fig_fore.add_trace(go.Scatter(
            x=hist_recent["date"],
            y=hist_recent["revpar"],
            name="Historical Daily RevPAR",
            line=dict(color="#2563EB", width=2)
        ))
        fig_fore.add_trace(go.Scatter(
            x=forecast_df["date"],
            y=forecast_df["forecasted_revpar"],
            name="30-Day ML Forecast",
            line=dict(color="#10B981", width=2.5, dash="dash")
        ))
        fig_fore.add_trace(go.Scatter(
            x=forecast_df["date"].tolist() + forecast_df["date"].tolist()[::-1],
            y=forecast_df["upper_bound"].tolist() + forecast_df["lower_bound"].tolist()[::-1],
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="Confidence Interval (±12%)"
        ))
        fig_fore.update_layout(
            title="Historical vs. Projected 30-Day RevPAR (₹)",
            xaxis_title="Date",
            yaxis_title="RevPAR (₹)",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig_fore, use_container_width=True)

    with ml_sub_tab3:
        st.markdown("#### Unsupervised K-Means Customer Clustering")
        st.markdown("Clusters booking records based on Lead Time, ADR, Length of Stay, and Guest Count.")

        clusters = mining_engine.perform_customer_clustering(n_clusters=3)
        st.dataframe(clusters, use_container_width=True)


# =============================================================
# TAB 5: DATA WAREHOUSE & STAR SCHEMA
# =============================================================
with tab5:
    st.subheader("Data Warehouse Architecture (Star Schema Specification)")
    st.markdown("""
    In accordance with dimensional modeling principles for Big Data Analytics, the pipeline normalizes raw PMS log feeds into a central **Star Schema**.
    """)

    schema_choice = st.selectbox(
        "Inspect Warehouse Table:",
        ["Dim_Property", "Dim_Date", "Dim_Room_Type", "Dim_Channel", "Dim_Customer_Segment", "Fact_Daily_Revenue", "Fact_Bookings"]
    )

    table_key_map = {
        "Dim_Property": "dim_property",
        "Dim_Date": "dim_date",
        "Dim_Room_Type": "dim_room_type",
        "Dim_Channel": "dim_channel",
        "Dim_Customer_Segment": "dim_customer_segment",
        "Fact_Daily_Revenue": "fact_daily_revenue",
        "Fact_Bookings": "fact_bookings"
    }

    selected_tbl = star_schema[table_key_map[schema_choice]]
    st.markdown(f"**Table Name:** `{schema_choice}` | **Total Records:** {len(selected_tbl)}")
    st.dataframe(selected_tbl.head(100), use_container_width=True)


# =============================================================
# TAB 6: WHAT-IF PRICING SIMULATOR
# =============================================================
with tab6:
    st.subheader("Revenue Manager What-If Pricing Simulator")
    st.markdown("Simulate how adjustments to the Average Daily Rate (ADR) impact occupancy and net yield.")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        price_adj_pct = st.slider("Simulated ADR Price Adjustment (%):", min_value=-25, max_value=25, value=5, step=1)
        price_elasticity = st.slider("Assumed Price Elasticity of Demand (PED):", min_value=-2.0, max_value=-0.2, value=-0.8, step=0.1)

    with sim_col2:
        current_adr = kpis["chain_adr"]
        current_occ = kpis["chain_occupancy_pct"]
        current_revpar = kpis["chain_revpar"]

        new_adr = current_adr * (1 + price_adj_pct / 100.0)
        delta_occ = current_occ * (price_elasticity * (price_adj_pct / 100.0))
        new_occ = max(10.0, min(100.0, current_occ + delta_occ))
        new_revpar = new_adr * (new_occ / 100.0)

        diff_revpar_pct = ((new_revpar - current_revpar) / current_revpar) * 100.0

        st.metric("New Simulated ADR", f"₹ {new_adr:,.2f}", f"{price_adj_pct:+.1f}%")
        st.metric("Estimated New Occupancy", f"{new_occ:.1f}%", f"{delta_occ:+.1f}% pts")
        st.metric("Resulting RevPAR", f"₹ {new_revpar:,.2f}", f"{diff_revpar_pct:+.2f}%")


# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.85rem;">
    <b>Project Title:</b> An OLAP-Based Revenue Analytics Pipeline for Hotel-Chain Revenue Data Mining<br>
    <b>Candidate:</b> BUDUPULA VIVEKA | <b>Guide:</b> Ms. G. Hema Sri | <b>Domain:</b> Big Data Analytics, Data Warehousing & Visualization
</div>
""", unsafe_allow_html=True)
