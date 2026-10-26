# An OLAP-Based Revenue Analytics Pipeline for Hotel-Chain Revenue Data Mining

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Data Warehouse](https://img.shields.io/badge/Data%20Warehouse-Star%20Schema-brightgreen.svg)]()
[![Domain](https://img.shields.io/badge/Domain-Big%20Data%20Analytics-orange.svg)]()

---

### Academic Project Details
* **Candidate Name:** BUDUPULA VIVEKA
* **Guide / Mentor:** Ms. G. Hema Sri
* **Domain / Area:** Big Data Analytics, Data Warehousing & Visualization
* **Keywords:** `hotel`, `chain`, `revenue`, `data mining`, `olap`, `star schema`, `revpar`, `adr`

---

## 📖 Abstract

In multi-property hospitality chains, disparate property management systems (PMS) generate fragmented booking records, hindering regional revenue managers from effectively comparing occupancy dynamics and yield performance. This project presents an end-to-end **OLAP-based revenue analytics pipeline** designed for hotel-chain revenue data mining.

Multi-property booking records undergo automated ETL cleaning, schema normalization, and dimensional modeling into a **Star Schema** data warehouse. An OLAP cube architecture enables multidimensional operations—such as **roll-up, drill-down, slicing, and dicing**—across dimensions including time, property location, room category, and distribution channel. Crucial hospitality metrics such as **RevPAR** (Revenue Per Available Room), **ADR** (Average Daily Rate), and **Occupancy Rate** are synthesized alongside data mining models for demand forecasting and cancellation risk prediction. The resulting intelligence is deployed via an interactive **Regional Revenue-Manager Dashboard** built on Streamlit, providing actionable decision support.

---

## 🏛️ System Architecture

```text
[ Multi-Property PMS Exports ]
               │
               ▼
[ 1. ETL & Cleansing Pipeline (etl_pipeline.py) ]
   ├── Schema Normalization & Key Generation
   ├── KPI Pre-aggregations (ADR, Occupancy, RevPAR)
   └── Dimension Extraction
               │
               ▼
[ 2. Data Warehouse: Star Schema ]
   ├── Fact_Daily_Revenue & Fact_Bookings
   └── Dimensions: Dim_Property, Dim_Date, Dim_Room_Type, Dim_Channel, Dim_Customer_Segment
               │
               ▼
[ 3. OLAP Cube & Data Mining Engine (olap_engine.py & data_mining.py) ]
   ├── Multidimensional Operations: Slice, Dice, Roll-up, Drill-down, Dynamic Pivot
   ├── Supervised Classification: Booking Cancellation Predictor (Random Forest)
   ├── Time-Series Forecasting: 30-Day RevPAR Demand Extrapolation
   └── Unsupervised Clustering: K-Means Customer Behavioral Segmentation
               │
               ▼
[ 4. Interactive Regional Revenue-Manager Dashboard (app.py) ]
   ├── Regional Executive KPI Cards & Yield Heatmaps
   ├── Multi-Property Benchmarking & Geo Breakdown
   ├── Interactive OLAP Matrix & What-If Pricing Simulator
```

---

## 🌟 Key Features

1. **Multidimensional OLAP Operations:**
   - **Roll-up:** Aggregate daily metrics $\rightarrow$ Monthly $\rightarrow$ Quarterly $\rightarrow$ Regional / Chain-wide.
   - **Drill-down:** De-aggregate from high-level Region down to specific properties and room categories.
   - **Slice & Dice:** Filter by geographic boundaries, customer segments, quarters, and booking channels.
   - **Dynamic Pivot Matrix:** Interactive cross-tabulation with heatmap color gradients.

2. **Hospitality Domain Key Performance Indicators (KPIs):**
   - **ADR (Average Daily Rate):** $\frac{\text{Total Room Revenue}}{\text{Rooms Sold}}$
   - **Occupancy Rate (%):** $\frac{\text{Rooms Sold}}{\text{Total Available Rooms}} \times 100$
   - **RevPAR (Revenue Per Available Room):** $\text{ADR} \times \text{Occupancy Rate}$

3. **Data Mining & Predictive Analytics:**
   - **Machine Learning Cancellation Classifier:** Evaluates incoming booking parameters and generates instant cancellation probability scoring (with ROC-AUC, Precision, Recall, and Feature Importance).
   - **30-Day RevPAR Forecaster:** Decomposes trend and day-of-week seasonality to predict forward yield.
   - **Customer Persona Segmentation:** K-Means clustering identifying distinct booking cohorts.
   - **What-If Pricing Simulator:** Dynamic price elasticity calculator for testing rate changes.

---

## 📁 Repository Structure

```
├── app.py                  # Streamlit Multi-Page Executive Revenue Dashboard
├── etl_pipeline.py         # Multi-property PMS data generator, ETL & Star Schema builder
├── olap_engine.py          # Multidimensional OLAP Cube operations (Slice, Dice, Roll-up, Drill-down, Pivot)
├── data_mining.py          # Random Forest cancellation classifier & time-series RevPAR forecaster
├── requirements.txt        # Python dependency manifest for local & cloud deployment
├── .gitignore              # Standard git exclusion rules
└── README.md               # Complete project documentation and guide
```

---

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/hotel-revenue-olap-pipeline.git
   cd hotel-revenue-olap-pipeline
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit Dashboard:**
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## ☁️ How to Deploy to Streamlit Community Cloud (Step-by-Step)

Follow these simple steps to deploy this application online for free:

### Step 1: Create a GitHub Repository
1. Log in to [GitHub](https://github.com/).
2. Click the **`+`** icon in the top right corner and select **New repository**.
3. Name your repository (e.g., `hotel-revenue-olap-pipeline`).
4. Set visibility to **Public** and leave other options unchecked.
5. Click **Create repository**.

### Step 2: Push the Code to GitHub
Run the following commands in your project folder terminal:
```bash
git init
git add .
git commit -m "Initial commit: Hotel-Chain OLAP Revenue Analytics Pipeline"
git branch -M main
git remote add origin https://github.com/<your-github-username>/hotel-revenue-olap-pipeline.git
git push -u origin main
```
*(Replace `<your-github-username>` with your actual GitHub username)*

### Step 3: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and click **Sign in with GitHub**.
2. Click **Create app** (or **New app**).
3. Fill in the deployment details:
   - **Repository:** `<your-github-username>/hotel-revenue-olap-pipeline`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** (Optional custom subdomain, e.g., `hotel-revenue-analytics`)
4. Click **Deploy!**
5. Streamlit will install the dependencies from `requirements.txt` and launch your live dashboard URL within 2 minutes!
