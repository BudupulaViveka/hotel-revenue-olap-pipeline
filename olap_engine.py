"""
OLAP Multidimensional Cube Engine
Project: An OLAP-Based Revenue Analytics Pipeline for Hotel-Chain Revenue Data Mining
Author: BUDUPULA VIVEKA
Mentor: Ms. G. Hema Sri
Domain: Big Data Analytics, Data Warehousing & Visualization
"""

import pandas as pd
import numpy as np


class HotelRevenueOLAPCube:
    """
    Multidimensional OLAP Cube for Hotel-Chain Revenue Data Mining.
    Executes Slice, Dice, Roll-up, Drill-down, and Pivot operations on Star Schema facts.
    """

    def __init__(self, star_schema: dict):
        self.dim_property = star_schema["dim_property"]
        self.dim_date = star_schema["dim_date"]
        self.dim_room_type = star_schema["dim_room_type"]
        self.dim_channel = star_schema["dim_channel"]
        self.dim_segment = star_schema["dim_customer_segment"]
        self.fact_bookings = star_schema["fact_bookings"]
        self.fact_daily_revenue = star_schema["fact_daily_revenue"]

        # Pre-denormalize unified analytical view for high-performance OLAP queries
        self._denormalized_view = self._build_cube_view()

    def _build_cube_view(self) -> pd.DataFrame:
        """Joins facts and dimensions into a denormalized multidimensional cube space."""
        df = self.fact_daily_revenue.merge(
            self.dim_property, on="property_id", how="left"
        ).merge(
            self.dim_room_type, on="room_type_id", how="left"
        ).merge(
            self.dim_date, on="date_id", how="left"
        )
        return df

    def get_cube(self) -> pd.DataFrame:
        """Returns the full denormalized OLAP cube DataFrame."""
        return self._denormalized_view.copy()

    def slice_cube(self, dimension_name: str, dimension_value) -> pd.DataFrame:
        """
        OLAP Slice Operation:
        Fixes one dimension to a single value to create a 2D sub-cube.
        e.g., Slicing by Region = 'South' or Year = 2025.
        """
        cube = self._denormalized_view
        if dimension_name not in cube.columns:
            raise ValueError(f"Dimension '{dimension_name}' not found in OLAP cube.")
        return cube[cube[dimension_name] == dimension_value].copy()

    def dice_cube(self, filters: dict) -> pd.DataFrame:
        """
        OLAP Dice Operation:
        Extracts a multi-dimensional sub-cube by applying multiple range or set filters.
        e.g., filters = {'region': ['South', 'West'], 'quarter': ['Q2', 'Q3'], 'tier': ['5-Star']}
        """
        cube = self._denormalized_view.copy()
        for col, values in filters.items():
            if col in cube.columns and values:
                if isinstance(values, list):
                    cube = cube[cube[col].isin(values)]
                else:
                    cube = cube[cube[col] == values]
        return cube

    def roll_up(self, group_by_dims: list, sub_cube: pd.DataFrame = None) -> pd.DataFrame:
        """
        OLAP Roll-up Operation:
        Aggregates measures across higher-level dimension hierarchies.
        Hierarchies:
          - Time: Day -> Month -> Quarter -> Year
          - Geography: Property -> City -> Region -> Chain
        """
        df = sub_cube if sub_cube is not None else self._denormalized_view

        agg_df = df.groupby(group_by_dims).agg(
            total_allocated_rooms=("allocated_rooms", "sum"),
            total_rooms_sold=("rooms_sold", "sum"),
            total_revenue=("room_revenue", "sum")
        ).reset_index()

        # Compute derived hospitality KPIs at aggregate level
        agg_df["avg_adr"] = (
            agg_df["total_revenue"] / agg_df["total_rooms_sold"].replace(0, np.nan)
        ).round(2).fillna(0)

        agg_df["avg_occupancy_pct"] = (
            (agg_df["total_rooms_sold"] / agg_df["total_allocated_rooms"].replace(0, np.nan)) * 100
        ).clip(0, 100).round(2).fillna(0)

        agg_df["avg_revpar"] = (
            agg_df["total_revenue"] / agg_df["total_allocated_rooms"].replace(0, np.nan)
        ).round(2).fillna(0)

        return agg_df

    def drill_down(self, parent_dim: str, child_dim: str, parent_value=None) -> pd.DataFrame:
        """
        OLAP Drill-down Operation:
        Navigates from higher-level summary down into finer granular detail.
        e.g., from Region -> Property, or Quarter -> Month.
        """
        df = self._denormalized_view
        if parent_value is not None:
            df = df[df[parent_dim] == parent_value]

        return self.roll_up(group_by_dims=[parent_dim, child_dim], sub_cube=df)

    def pivot_cube(self, index_dim: str, column_dim: str, metric: str = "avg_revpar", sub_cube: pd.DataFrame = None) -> pd.DataFrame:
        """
        OLAP Pivot Operation:
        Rotates dimensions to present a cross-tabulation matrix of hospitality metrics.
        """
        rolled_up = self.roll_up(group_by_dims=[index_dim, column_dim], sub_cube=sub_cube)
        pivot = rolled_up.pivot_table(
            index=index_dim,
            columns=column_dim,
            values=metric,
            aggfunc="mean"
        ).fillna(0).round(2)
        return pivot

    def calculate_chain_kpis(self, sub_cube: pd.DataFrame = None) -> dict:
        """
        Computes chain-wide core revenue management KPIs:
        ADR, Occupancy Rate, RevPAR, Total Gross Revenue, Total Rooms Sold.
        """
        df = sub_cube if sub_cube is not None else self._denormalized_view
        tot_rooms_sold = df["rooms_sold"].sum()
        tot_allocated = df["allocated_rooms"].sum()
        tot_revenue = df["room_revenue"].sum()

        adr = round(tot_revenue / tot_rooms_sold, 2) if tot_rooms_sold > 0 else 0
        occ = round((tot_rooms_sold / tot_allocated) * 100, 2) if tot_allocated > 0 else 0
        revpar = round(tot_revenue / tot_allocated, 2) if tot_allocated > 0 else 0

        return {
            "total_revenue": tot_revenue,
            "total_rooms_sold": int(tot_rooms_sold),
            "total_rooms_available": int(tot_allocated),
            "chain_adr": adr,
            "chain_occupancy_pct": occ,
            "chain_revpar": revpar
        }
