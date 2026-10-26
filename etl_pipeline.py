"""
ETL Pipeline & Data Warehouse Dimensional Modeling (Star Schema)
Project: An OLAP-Based Revenue Analytics Pipeline for Hotel-Chain Revenue Data Mining
Author: BUDUPULA VIVEKA
Mentor: Ms. G. Hema Sri
Domain: Big Data Analytics, Data Warehousing & Visualization
"""

import datetime
import numpy as np
import pandas as pd


def generate_raw_booking_exports(n_records: int = 10000, seed: int = 42) -> pd.DataFrame:
    """
    Simulates multi-property Property Management System (PMS) booking system raw exports.
    Includes booking metadata, stay details, distribution channels, and cancellation flags.
    """
    np.random.seed(seed)

    properties = [
        {"property_id": "PROP_01", "name": "Grand Palace Hotel", "region": "South", "city": "Hyderabad", "tier": "5-Star", "capacity": 220},
        {"property_id": "PROP_02", "name": "Silicon Heights", "region": "South", "city": "Bengaluru", "tier": "4-Star", "capacity": 180},
        {"property_id": "PROP_03", "name": "Marina Breeze Resort", "region": "South", "city": "Chennai", "tier": "4-Star", "capacity": 150},
        {"property_id": "PROP_04", "name": "Gateway Sovereign", "region": "West", "city": "Mumbai", "tier": "5-Star", "capacity": 250},
        {"property_id": "PROP_05", "name": "Imperial Heritage", "region": "North", "city": "Delhi NCR", "tier": "5-Star", "capacity": 210},
        {"property_id": "PROP_06", "name": "Sunset Coastline Resort", "region": "West", "city": "Goa", "tier": "4-Star", "capacity": 130},
    ]

    room_types = [
        {"room_type_id": "ROOM_STD", "room_type": "Standard Room", "base_rate": 3500},
        {"room_type_id": "ROOM_DLX", "room_type": "Deluxe Room", "base_rate": 5500},
        {"room_type_id": "ROOM_EXE", "room_type": "Executive Suite", "base_rate": 8500},
        {"room_type_id": "ROOM_PRS", "room_type": "Presidential Suite", "base_rate": 16000},
    ]

    channels = [
        {"channel_id": "CHN_DIR", "channel_name": "Direct Website", "commission_pct": 0.0},
        {"channel_id": "CHN_OTA_BKG", "channel_name": "OTA (Booking.com)", "commission_pct": 18.0},
        {"channel_id": "CHN_OTA_MMT", "channel_name": "OTA (MakeMyTrip / Expedia)", "commission_pct": 16.0},
        {"channel_id": "CHN_CORP", "channel_name": "Corporate Contract", "commission_pct": 8.0},
        {"channel_id": "CHN_WALK", "channel_name": "Walk-In / Direct Call", "commission_pct": 0.0},
    ]

    segments = ["Business", "Leisure", "Family Vacation", "Conference / Group"]

    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    records = []
    booking_counter = 10001

    for _ in range(n_records):
        prop = np.random.choice(properties)
        room = np.random.choice(room_types, p=[0.45, 0.35, 0.15, 0.05])
        channel = np.random.choice(channels, p=[0.25, 0.30, 0.22, 0.15, 0.08])
        segment = np.random.choice(segments, p=[0.35, 0.35, 0.20, 0.10])

        random_day_offset = np.random.randint(0, total_days)
        checkin_date = start_date + datetime.timedelta(days=int(random_day_offset))
        lead_time = int(np.random.exponential(scale=18))
        booking_date = checkin_date - datetime.timedelta(days=lead_time)

        nights = int(np.random.choice([1, 2, 3, 4, 5, 7], p=[0.35, 0.35, 0.15, 0.08, 0.05, 0.02]))
        checkout_date = checkin_date + datetime.timedelta(days=nights)

        is_weekend = checkin_date.weekday() >= 5
        season_multiplier = 1.0
        if checkin_date.month in [11, 12, 1]:
            season_multiplier = 1.25 if prop["region"] in ["West", "South"] else 1.15
        elif checkin_date.month in [5, 6]:
            season_multiplier = 0.90

        weekend_multiplier = 1.20 if is_weekend else 1.0
        city_multiplier = 1.15 if prop["tier"] == "5-Star" else 1.0

        random_fluctuation = np.random.uniform(0.92, 1.12)
        adr = round(room["base_rate"] * season_multiplier * weekend_multiplier * city_multiplier * random_fluctuation, 2)
        gross_revenue = round(adr * nights, 2)
        commission_amount = round(gross_revenue * (channel["commission_pct"] / 100.0), 2)
        net_revenue = round(gross_revenue - commission_amount, 2)

        # Cancellation probability driven by lead time and channel
        cancel_prob = 0.12
        if lead_time > 30:
            cancel_prob += 0.18
        if "OTA" in channel["channel_name"]:
            cancel_prob += 0.08
        if segment == "Business":
            cancel_prob -= 0.05

        cancel_prob = max(0.02, min(0.65, cancel_prob))
        is_cancelled = 1 if np.random.rand() < cancel_prob else 0

        num_guests = int(np.random.choice([1, 2, 3, 4], p=[0.40, 0.45, 0.10, 0.05]))

        records.append({
            "booking_id": f"BKG_{booking_counter}",
            "booking_date": booking_date,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "property_id": prop["property_id"],
            "property_name": prop["name"],
            "region": prop["region"],
            "city": prop["city"],
            "tier": prop["tier"],
            "capacity": prop["capacity"],
            "room_type_id": room["room_type_id"],
            "room_type": room["room_type"],
            "channel_id": channel["channel_id"],
            "channel_name": channel["channel_name"],
            "commission_pct": channel["commission_pct"],
            "customer_segment": segment,
            "lead_time": lead_time,
            "nights": nights,
            "num_guests": num_guests,
            "adr": adr,
            "gross_revenue": gross_revenue,
            "commission_amount": commission_amount,
            "net_revenue": net_revenue,
            "is_cancelled": is_cancelled
        })
        booking_counter += 1

    df = pd.DataFrame(records)
    return df


def build_star_schema(raw_df: pd.DataFrame):
    """
    Extract, Transform, and Load (ETL) raw PMS booking logs into a multidimensional Star Schema.
    Returns:
        dim_property, dim_date, dim_room_type, dim_channel, dim_customer_segment, fact_bookings, fact_daily_revenue
    """
    # 1. Dim_Property
    dim_property = raw_df[[
        "property_id", "property_name", "region", "city", "tier", "capacity"
    ]].drop_duplicates().reset_index(drop=True)

    # 2. Dim_Room_Type
    dim_room_type = raw_df[[
        "room_type_id", "room_type"
    ]].drop_duplicates().reset_index(drop=True)

    # 3. Dim_Channel
    dim_channel = raw_df[[
        "channel_id", "channel_name", "commission_pct"
    ]].drop_duplicates().reset_index(drop=True)

    # 4. Dim_Customer_Segment
    dim_customer_segment = pd.DataFrame({
        "segment_id": [f"SEG_{i+1:02d}" for i in range(len(raw_df["customer_segment"].unique()))],
        "segment_name": raw_df["customer_segment"].unique()
    })
    seg_map = dict(zip(dim_customer_segment["segment_name"], dim_customer_segment["segment_id"]))
    raw_df["segment_id"] = raw_df["customer_segment"].map(seg_map)

    # 5. Dim_Date (based on checkin_date)
    min_date = raw_df["checkin_date"].min()
    max_date = raw_df["checkin_date"].max()
    date_range = pd.date_range(min_date, max_date, freq="D")

    dim_date = pd.DataFrame({
        "date_id": [d.strftime("%Y%m%d") for d in date_range],
        "full_date": date_range.date,
        "year": date_range.year,
        "quarter": [f"Q{q}" for q in date_range.quarter],
        "month": date_range.month_name(),
        "month_num": date_range.month,
        "day": date_range.day,
        "day_of_week": date_range.day_name(),
        "is_weekend": [1 if d.weekday() >= 5 else 0 for d in date_range],
        "season": [
            "Winter" if m in [12, 1, 2] else "Summer" if m in [3, 4, 5, 6] else "Monsoon/Autumn"
            for m in date_range.month
        ]
    })
    date_map = dict(zip(dim_date["full_date"], dim_date["date_id"]))
    raw_df["date_id"] = raw_df["checkin_date"].map(date_map)

    # 6. Fact_Bookings (Granular transactional fact)
    fact_bookings = raw_df[[
        "booking_id", "date_id", "property_id", "room_type_id", "channel_id", "segment_id",
        "lead_time", "nights", "num_guests", "adr", "gross_revenue", "commission_amount",
        "net_revenue", "is_cancelled"
    ]].copy()

    # 7. Fact_Daily_Revenue (Aggregated multi-property daily revenue fact table for OLAP)
    confirmed_df = raw_df[raw_df["is_cancelled"] == 0].copy()

    # Expand confirmed bookings over their stay dates to accurately compute daily rooms occupied
    stay_records = []
    for _, row in confirmed_df.iterrows():
        checkin = row["checkin_date"]
        for day_i in range(row["nights"]):
            current_day = checkin + datetime.timedelta(days=day_i)
            stay_records.append({
                "date": current_day,
                "property_id": row["property_id"],
                "room_type_id": row["room_type_id"],
                "channel_id": row["channel_id"],
                "daily_revenue": row["adr"],
                "room_sold": 1
            })

    daily_stays_df = pd.DataFrame(stay_records)

    # Group daily aggregates
    daily_agg = daily_stays_df.groupby(["date", "property_id", "room_type_id"]).agg(
        rooms_sold=("room_sold", "sum"),
        room_revenue=("daily_revenue", "sum")
    ).reset_index()

    # Merge property capacity to compute Occupancy & RevPAR
    daily_agg = daily_agg.merge(dim_property[["property_id", "capacity"]], on="property_id", how="left")
    daily_agg["date_id"] = daily_agg["date"].map(date_map)

    # Standard hospitality KPIs:
    # ADR = Revenue / Rooms Sold
    daily_agg["adr"] = (daily_agg["room_revenue"] / daily_agg["rooms_sold"]).round(2)
    # Estimated room type capacity allocation: 40% STD, 35% DLX, 15% EXE, 10% PRS
    capacity_weights = {"ROOM_STD": 0.40, "ROOM_DLX": 0.35, "ROOM_EXE": 0.15, "ROOM_PRS": 0.10}
    daily_agg["allocated_rooms"] = daily_agg.apply(
        lambda r: int(round(r["capacity"] * capacity_weights.get(r["room_type_id"], 0.25))), axis=1
    )
    daily_agg["occupancy_rate_pct"] = (
        (daily_agg["rooms_sold"] / daily_agg["allocated_rooms"].replace(0, 1)) * 100
    ).clip(0, 100).round(2)
    # RevPAR = ADR * Occupancy Rate or Room Revenue / Allocated Rooms
    daily_agg["revpar"] = (
        daily_agg["room_revenue"] / daily_agg["allocated_rooms"].replace(0, 1)
    ).round(2)

    fact_daily_revenue = daily_agg[[
        "date_id", "date", "property_id", "room_type_id", "allocated_rooms",
        "rooms_sold", "room_revenue", "occupancy_rate_pct", "adr", "revpar"
    ]].dropna()

    return {
        "dim_property": dim_property,
        "dim_date": dim_date,
        "dim_room_type": dim_room_type,
        "dim_channel": dim_channel,
        "dim_customer_segment": dim_customer_segment,
        "fact_bookings": fact_bookings,
        "fact_daily_revenue": fact_daily_revenue,
        "raw_dataset": raw_df
    }


if __name__ == "__main__":
    print("[ETL] Synthesizing multi-property booking exports...")
    raw = generate_raw_booking_exports(n_records=3000)
    print(f"[ETL] Total raw booking records generated: {len(raw)}")
    schema = build_star_schema(raw)
    print("[ETL] Star Schema built successfully:")
    for key, table in schema.items():
        if key != "raw_dataset":
            print(f"  - {key}: {len(table)} records")
