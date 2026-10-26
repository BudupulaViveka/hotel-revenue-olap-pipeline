"""
Data Mining & Machine Learning Pipeline
Project: An OLAP-Based Revenue Analytics Pipeline for Hotel-Chain Revenue Data Mining
Author: BUDUPULA VIVEKA
Mentor: Ms. G. Hema Sri
Domain: Big Data Analytics, Data Warehousing & Visualization
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


class HotelDataMiningEngine:
    """
    Data Mining module containing:
    1. Booking Cancellation Prediction Model (Supervised Classification)
    2. RevPAR & Demand Forecaster (Time-Series Extrapolation)
    3. Customer Behavioral Segmentation (Unsupervised K-Means Clustering)
    """

    def __init__(self, raw_bookings: pd.DataFrame):
        self.raw_df = raw_bookings.copy()
        self.classification_pipeline = None
        self.feature_importance_df = None
        self.model_metrics = {}
        self.kmeans_model = None
        self.cluster_scaler = None

    def train_cancellation_model(self):
        """
        Trains a Random Forest classifier to predict booking cancellations based on
        lead time, booking channel, pricing (ADR), room category, and guest segment.
        """
        features = [
            "lead_time", "nights", "num_guests", "adr",
            "region", "tier", "room_type", "channel_name", "customer_segment"
        ]
        target = "is_cancelled"

        X = self.raw_df[features].copy()
        y = self.raw_df[target].copy()

        numeric_features = ["lead_time", "nights", "num_guests", "adr"]
        categorical_features = ["region", "tier", "room_type", "channel_name", "customer_segment"]

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_features)
            ]
        )

        model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)

        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", model)
        ])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        self.model_metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred), 4),
            "recall": round(recall_score(y_test, y_pred), 4),
            "f1": round(f1_score(y_test, y_pred), 4),
            "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
            "test_sample_count": len(y_test)
        }

        # Extract feature importances
        cat_encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"]
        encoded_cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
        all_features = numeric_features + encoded_cat_names
        importances = pipeline.named_steps["classifier"].feature_importances_

        feat_df = pd.DataFrame({
            "feature": all_features,
            "importance": importances
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)

        self.classification_pipeline = pipeline
        self.feature_importance_df = feat_df
        return self.model_metrics

    def predict_single_booking(self, input_dict: dict) -> dict:
        """
        Scores a prospective incoming booking record to estimate its probability of cancellation.
        """
        if self.classification_pipeline is None:
            self.train_cancellation_model()

        input_df = pd.DataFrame([input_dict])
        prob = self.classification_pipeline.predict_proba(input_df)[0][1]
        pred = int(prob >= 0.50)

        risk_level = "High Risk" if prob >= 0.60 else "Moderate Risk" if prob >= 0.35 else "Low Risk"

        return {
            "cancellation_probability": round(prob * 100, 2),
            "predicted_cancellation": pred,
            "risk_level": risk_level
        }

    def forecast_revpar(self, daily_df: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
        """
        Time-series data mining: extrapolates daily RevPAR and demand using
        polynomial trend and day-of-week seasonality decomposition.
        """
        # Aggregate daily total revenue and allocated rooms across the selection
        daily_ts = daily_df.groupby("date").agg(
            revenue=("room_revenue", "sum"),
            capacity=("allocated_rooms", "sum")
        ).reset_index()

        daily_ts["revpar"] = (daily_ts["revenue"] / daily_ts["capacity"]).round(2)
        daily_ts["date"] = pd.to_datetime(daily_ts["date"])
        daily_ts = daily_ts.sort_values("date").reset_index(drop=True)

        n = len(daily_ts)
        x = np.arange(n)
        y = daily_ts["revpar"].values

        # Linear + Seasonal trend fit
        poly_coeff = np.polyfit(x, y, deg=1)
        trend = np.polyval(poly_coeff, x)

        # Day-of-week seasonal factors
        daily_ts["dow"] = daily_ts["date"].dt.dayofweek
        daily_ts["residual"] = y - trend
        dow_seasonality = daily_ts.groupby("dow")["residual"].mean().to_dict()

        # Forecast forward
        last_date = daily_ts["date"].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, days_ahead + 1)]
        future_x = np.arange(n, n + days_ahead)
        future_trend = np.polyval(poly_coeff, future_x)

        forecast_vals = []
        for d, t_val in zip(future_dates, future_trend):
            dow = d.dayofweek
            seas = dow_seasonality.get(dow, 0)
            noise = np.random.normal(0, np.std(daily_ts["residual"]) * 0.4)
            forecast_revpar = max(500, round(t_val + seas + noise, 2))
            forecast_vals.append(forecast_revpar)

        forecast_df = pd.DataFrame({
            "date": future_dates,
            "forecasted_revpar": forecast_vals,
            "lower_bound": [round(val * 0.88, 2) for val in forecast_vals],
            "upper_bound": [round(val * 1.12, 2) for val in forecast_vals]
        })

        return forecast_df

    def perform_customer_clustering(self, n_clusters: int = 3) -> pd.DataFrame:
        """
        Unsupervised K-Means clustering on booking behaviors to extract actionable guest personas.
        """
        cluster_cols = ["lead_time", "nights", "num_guests", "adr"]
        cluster_data = self.raw_df[cluster_cols].dropna().copy()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(cluster_data)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        cluster_data["cluster_id"] = [f"Segment {c+1}" for c in cluster_labels]

        profile = cluster_data.groupby("cluster_id").agg(
            count=("lead_time", "count"),
            avg_lead_time=("lead_time", "mean"),
            avg_nights=("nights", "mean"),
            avg_guests=("num_guests", "mean"),
            avg_adr=("adr", "mean")
        ).round(2).reset_index()

        persona_names = {
            0: "Corporate / Short Stay",
            1: "Advance Leisure / Family",
            2: "Premium Luxury Extended"
        }
        profile["persona_type"] = [persona_names.get(i, f"Cluster {i+1}") for i in range(len(profile))]
        return profile
