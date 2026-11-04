import pandas as pd
from typing import Tuple

class PriceAnalyzer:
    @staticmethod
    def compare_snapshots(previous_df: pd.DataFrame, current_df: pd.DataFrame) -> pd.DataFrame:
        """Compares two data snapshots and calculates price deltas."""
        if previous_df.empty:
            current_df["status"] = "NEW"
            current_df["price_change"] = 0.0
            current_df["old_price"] = current_df["price"]
            return current_df

        merged = pd.merge(
            current_df, 
            previous_df[["sku", "price"]], 
            on="sku", 
            how="outer", 
            suffixes=("", "_old")
        )

        def determine_status(row):
            if pd.isna(row["price_old"]):
                return "NEW PRODUCT"
            if pd.isna(row["price"]):
                return "REMOVED"
            if row["price"] < row["price_old"]:
                return "PRICE DROP"
            if row["price"] > row["price_old"]:
                return "PRICE INCREASE"
            return "UNCHANGED"

        merged["status"] = merged.apply(determine_status, axis=1)
        merged["old_price"] = merged["price_old"].fillna(merged["price"])
        merged["price_change"] = merged["price"] - merged["old_price"]
        
        return merged