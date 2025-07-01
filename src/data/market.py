# src/data/market.py
import os
from typing import List
import pandas as pd
from api.epias import EpiasClient


def _client() -> EpiasClient:
    return EpiasClient(os.environ["EPIAS_USER"], os.environ["EPIAS_PASS"])


def clearing_quantity(
    *,
    start: str,
    end: str,
    power_plant_id: int,      # NOTE: docs say organisationId, sample uses powerPlantId
) -> pd.DataFrame:
    """
    Fetch DAM matched bid / offer quantities (hourly) for a single plant.

    Parameters
    ----------
    start, end : ISO 8601 strings with timezone (YYYY-MM-DDTHH:MM:SS+03:00)
    power_plant_id : int  (use organisationId=<id> if the endpoint actually requires it)

    Returns
    -------
    tidy pandas.DataFrame indexed by tz-aware timestamp,
    columns = ['matchedBids', 'matchedOffers']
    """
    path = "/markets/dam/data/clearing-quantity"
    payload = {
        "startDate": start,
        "endDate": end,
        "powerPlantId": power_plant_id,     # swap key to organisationId if needed
    }
    data = _client().post(path, **payload)

    # -- 1️⃣ normalise JSON to rows -------------------------------------- #
    df = pd.DataFrame(data["items"])
    if df.empty:
        return df  # nothing fetched

    # -- 2️⃣ unify date & hour into a single tz-aware timestamp ---------- #
    df["ts"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df = df.set_index("ts").drop(columns=["date", "hour"])

    # -- 3️⃣ keep numeric columns as floats ----------------------------- #
    df = df.astype({"matchedBids": "float64", "matchedOffers": "float64"})
    return df.sort_index()
