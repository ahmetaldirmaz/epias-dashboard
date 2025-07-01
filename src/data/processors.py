"""
Data processors for transforming API responses to DataFrames
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Process raw API data into pandas DataFrames
    """

    @staticmethod
    def extract_content(response: Union[Dict, List]) -> List[Dict]:
        """Extract content from API response"""
        if isinstance(response, list):
            return response

        if isinstance(response, dict):
            if "body" in response and "content" in response["body"]:
                return response["body"]["content"]
            elif "content" in response:
                return response["content"]
            elif "items" in response:
                return response["items"]

        return [response] if response else []

    @staticmethod
    def parse_datetime(dt_str: str) -> pd.Timestamp:
        """Parse datetime string to pandas Timestamp"""
        try:
            # Handle different datetime formats
            if "T" in dt_str:
                return pd.to_datetime(dt_str)
            else:
                return pd.to_datetime(dt_str, format="%Y-%m-%d")
        except:
            return pd.NaT

    def process_ptf_data(self, data: Union[Dict, List]) -> pd.DataFrame:
        """
        Process PTF (Piyasa Takas Fiyatı) data

        Args:
            data: Raw API response

        Returns:
            DataFrame with columns: datetime, price, hour
        """
        content = self.extract_content(data)

        if not content:
            return pd.DataFrame(columns=["datetime", "price", "hour"])

        records = []
        for item in content:
            if isinstance(item, dict):
                dt = self.parse_datetime(item.get("date", ""))
                records.append({
                    "datetime": dt,
                    "price": float(item.get("price", 0) or item.get("value", 0)),
                    "hour": int(item.get("hour", dt.hour if pd.notna(dt) else 0))
                })

        df = pd.DataFrame(records)
        df = df.sort_values("datetime")
        df = df.set_index("datetime")

        logger.info(f"Processed PTF data: {len(df)} records")
        return df

    def process_smf_data(self, data: Union[Dict, List]) -> pd.DataFrame:
        """
        Process SMF (Sistem Marjinal Fiyatı) data

        Args:
            data: Raw API response

        Returns:
            DataFrame with columns: datetime, up_price, down_price, direction
        """
        content = self.extract_content(data)

        if not content:
            return pd.DataFrame(columns=["datetime", "up_price", "down_price", "direction"])

        records = []
        for item in content:
            if isinstance(item, dict):
                dt = self.parse_datetime(item.get("date", ""))
                records.append({
                    "datetime": dt,
                    "up_price": float(item.get("upRegulationPrice", 0) or item.get("yalPrice", 0)),
                    "down_price": float(item.get("downRegulationPrice", 0) or item.get("yatPrice", 0)),
                    "direction": item.get("systemDirection", "")
                })

        df = pd.DataFrame(records)
        df = df.sort_values("datetime")
        df = df.set_index("datetime")

        logger.info(f"Processed SMF data: {len(df)} records")
        return df

    def process_generation_data(self, data: Union[Dict, List]) -> pd.DataFrame:
        """
        Process generation data

        Args:
            data: Raw API response

        Returns:
            DataFrame with generation data by power plant and type
        """
        content = self.extract_content(data)

        if not content:
            return pd.DataFrame(columns=["datetime", "power_plant", "type", "value"])

        records = []
        for item in content:
            if isinstance(item, dict):
                dt = self.parse_datetime(item.get("date", ""))

                # Handle different response formats
                if "hourlyGenerations" in item:
                    # Hourly data
                    for hour_data in item["hourlyGenerations"]:
                        records.append({
                            "datetime": dt.replace(hour=int(hour_data.get("hour", 0))),
                            "power_plant": item.get("powerPlantName", ""),
                            "power_plant_id": item.get("powerPlantId"),
                            "type": hour_data.get("generationType", ""),
                            "value": float(hour_data.get("generation", 0))
                        })
                else:
                    # Simple format
                    records.append({
                        "datetime": dt,
                        "power_plant": item.get("powerPlantName", ""),
                        "power_plant_id": item.get("powerPlantId"),
                        "type": item.get("generationType", ""),
                        "value": float(item.get("generation", 0) or item.get("value", 0))
                    })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("datetime")
            df = df.set_index("datetime")

        logger.info(f"Processed generation data: {len(df)} records")
        return df

    def process_kgup_data(self, data: Union[Dict, List]) -> pd.DataFrame:
        """
        Process KGÜP (Kesinleşmiş Günlük Üretim Planı) data

        Args:
            data: Raw API response

        Returns:
            DataFrame with KGÜP data
        """
        content = self.extract_content(data)

        if not content:
            return pd.DataFrame(columns=["datetime", "uevcb", "planned_generation"])

        records = []
        for item in content:
            if isinstance(item, dict):
                dt = self.parse_datetime(item.get("date", ""))

                if "hourlyPlans" in item:
                    for hour_data in item["hourlyPlans"]:
                        records.append({
                            "datetime": dt.replace(hour=int(hour_data.get("hour", 0))),
                            "uevcb": item.get("uevcbName", ""),
                            "uevcb_id": item.get("uevcbId"),
                            "planned_generation": float(hour_data.get("plannedGeneration", 0))
                        })
                else:
                    records.append({
                        "datetime": dt,
                        "uevcb": item.get("uevcbName", ""),
                        "uevcb_id": item.get("uevcbId"),
                        "planned_generation": float(item.get("plannedGeneration", 0) or item.get("value", 0))
                    })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("datetime")
            df = df.set_index("datetime")

        logger.info(f"Processed KGÜP data: {len(df)} records")
        return df

    def process_bilateral_contracts(
            self,
            buy_data: Union[Dict, List],
            sell_data: Union[Dict, List]
    ) -> pd.DataFrame:
        """
        Process bilateral contracts data

        Args:
            buy_data: Buy side data
            sell_data: Sell side data

        Returns:
            DataFrame with bilateral contracts
        """
        buy_content = self.extract_content(buy_data)
        sell_content = self.extract_content(sell_data)

        records = []

        # Process buy data
        for item in buy_content:
            if isinstance(item, dict):
                dt = self.parse_datetime(item.get("date", ""))
                records.append({
                    "datetime": dt,
                    "type": "buy",
                    "contract_type": item.get("contractType", ""),
                    "quantity": float(item.get("quantity", 0) or item.get("value", 0))
                })

        # Process sell data
        for item in sell_content:
            if isinstance(item, dict):
                dt = self.parse_datetime(item.get("date", ""))
                records.append({
                    "datetime": dt,
                    "type": "sell",
                    "contract_type": item.get("contractType", ""),
                    "quantity": float(item.get("quantity", 0) or item.get("value", 0))
                })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("datetime")
            df = df.pivot_table(
                index="datetime",
                columns=["type", "contract_type"],
                values="quantity",
                fill_value=0
            )

        logger.info(f"Processed bilateral contracts: {len(df)} records")
        return df

    def process_consumption_data(self, data: Union[Dict, List]) -> pd.DataFrame:
        """
        Process consumption data

        Args:
            data: Raw API response

        Returns:
            DataFrame with consumption data
        """
        content = self.extract_content(data)

        if not content:
            return pd.DataFrame(columns=["datetime", "province", "district", "profile_group", "value"])

        records = []
        for item in content:
            if isinstance(item, dict):
                dt = self.parse_datetime(item.get("date", ""))
                records.append({
                    "datetime": dt,
                    "province": item.get("province", ""),
                    "district": item.get("district", ""),
                    "profile_group": item.get("profileGroup", ""),
                    "subscriber_type": item.get("subscriberType", ""),
                    "value": float(item.get("consumption", 0) or item.get("value", 0))
                })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("datetime")
            df = df.set_index("datetime")

        logger.info(f"Processed consumption data: {len(df)} records")
        return df

    def process_dashboard_data(self, data: Dict) -> pd.DataFrame:
        """
        Process dashboard summary data

        Args:
            data: Raw API response

        Returns:
            DataFrame with dashboard metrics
        """
        if not data or "body" not in data:
            return pd.DataFrame()

        body = data["body"]
        records = []

        # Extract different dashboard formats
        if "summary" in body:
            for metric, value in body["summary"].items():
                records.append({
                    "metric": metric,
                    "value": value,
                    "timestamp": datetime.now()
                })

        elif "data" in body:
            for item in body["data"]:
                if isinstance(item, dict):
                    records.append({
                        "metric": item.get("name", ""),
                        "value": item.get("value", 0),
                        "change": item.get("change", 0),
                        "timestamp": self.parse_datetime(item.get("date", ""))
                    })

        df = pd.DataFrame(records)
        logger.info(f"Processed dashboard data: {len(df)} records")
        return df

    def aggregate_generation_by_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate generation data by type

        Args:
            df: Generation DataFrame

        Returns:
            Aggregated DataFrame by generation type
        """
        if df.empty:
            return pd.DataFrame()

        return df.groupby(["type"])["value"].agg([
            ("total", "sum"),
            ("mean", "mean"),
            ("max", "max"),
            ("min", "min")
        ]).round(2)

    def calculate_price_statistics(self, df: pd.DataFrame, price_col: str = "price") -> Dict[str, float]:
        """
        Calculate price statistics

        Args:
            df: DataFrame with price data
            price_col: Name of price column

        Returns:
            Dictionary with statistics
        """
        if df.empty or price_col not in df.columns:
            return {}

        return {
            "mean": df[price_col].mean(),
            "median": df[price_col].median(),
            "std": df[price_col].std(),
            "min": df[price_col].min(),
            "max": df[price_col].max(),
            "volatility": (df[price_col].std() / df[price_col].mean()) * 100 if df[price_col].mean() > 0 else 0
        }