"""
Data fetchers for EPİAŞ API
"""
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import pandas as pd

from src.api.epias import EPIASClient, APIError
from src.api.endpoints import APIEndpoints
from src.data.models import (
    Organization, PowerPlant, UEVCB,
    DateRangeRequest, OrganizationRequest,
    GenerationDataRequest, MarketDataRequest,
    BilateralContractsRequest, ConsumptionDataRequest,
    OrganizationListRequest, PowerPlantListRequest,
    UEVCBListRequest
)
from src.data.processors import DataProcessor

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    High-level data fetching interface for EPİAŞ API
    """

    def __init__(self, client: Optional[EPIASClient] = None):
        self.client = client or EPIASClient()
        self.processor = DataProcessor()

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    # Organization and Power Plant fetchers
    async def fetch_organizations(
            self,
            start_date: date,
            end_date: date
    ) -> List[Organization]:
        """
        Fetch all organizations for date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of organizations
        """
        request = OrganizationListRequest(
            startDate=datetime.combine(start_date, datetime.min.time()),
            endDate=datetime.combine(end_date, datetime.max.time())
        )

        try:
            response = await self.client.post(
                APIEndpoints.GENERATION_ORG_LIST,
                request.dict()
            )

            organizations = []
            if "body" in response and "organizations" in response["body"]:
                for org_data in response["body"]["organizations"]:
                    organizations.append(Organization(**org_data))

            logger.info(f"Fetched {len(organizations)} organizations")
            return organizations

        except APIError as e:
            logger.error(f"Failed to fetch organizations: {e}")
            raise

    async def fetch_power_plants(self) -> List[PowerPlant]:
        """
        Fetch all power plants

        Returns:
            List of power plants
        """
        try:
            response = await self.client.get(APIEndpoints.GENERATION_POWERPLANT_LIST)

            power_plants = []
            if "body" in response and "powerPlantList" in response["body"]:
                for pp_data in response["body"]["powerPlantList"]:
                    power_plants.append(PowerPlant(**pp_data))

            logger.info(f"Fetched {len(power_plants)} power plants")
            return power_plants

        except APIError as e:
            logger.error(f"Failed to fetch power plants: {e}")
            raise

    async def fetch_uevcb_list(self, organization_id: int) -> List[UEVCB]:
        """
        Fetch UEVCB list for an organization

        Args:
            organization_id: Organization ID

        Returns:
            List of UEVCBs
        """
        request = UEVCBListRequest(organizationId=organization_id)

        try:
            response = await self.client.post(
                APIEndpoints.GENERATION_UEVCB_LIST,
                request.dict()
            )

            uevcb_list = []
            if "body" in response and "uevcbList" in response["body"]:
                for uevcb_data in response["body"]["uevcbList"]:
                    uevcb_list.append(UEVCB(**uevcb_data))

            logger.info(f"Fetched {len(uevcb_list)} UEVCBs for org {organization_id}")
            return uevcb_list

        except APIError as e:
            logger.error(f"Failed to fetch UEVCB list: {e}")
            raise

    # Market Data fetchers
    async def fetch_ptf_data(
            self,
            start_date: date,
            end_date: date
    ) -> pd.DataFrame:
        """
        Fetch PTF (Piyasa Takas Fiyatı) data

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with PTF data
        """
        request = MarketDataRequest(
            startDate=datetime.combine(start_date, datetime.min.time()),
            endDate=datetime.combine(end_date, datetime.max.time())
        )

        try:
            data = await self.client.get_paginated(
                APIEndpoints.DAM_MCP,
                request.dict()
            )

            df = self.processor.process_ptf_data(data)
            logger.info(f"Fetched PTF data: {len(df)} records")
            return df

        except APIError as e:
            logger.error(f"Failed to fetch PTF data: {e}")
            raise

    async def fetch_smf_data(
            self,
            start_date: date,
            end_date: date
    ) -> pd.DataFrame:
        """
        Fetch SMF (Sistem Marjinal Fiyatı) data

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with SMF data
        """
        request = MarketDataRequest(
            startDate=datetime.combine(start_date, datetime.min.time()),
            endDate=datetime.combine(end_date, datetime.max.time())
        )

        try:
            data = await self.client.get_paginated(
                APIEndpoints.BPM_SYSTEM_MARGINAL_PRICE,
                request.dict()
            )

            df = self.processor.process_smf_data(data)
            logger.info(f"Fetched SMF data: {len(df)} records")
            return df

        except APIError as e:
            logger.error(f"Failed to fetch SMF data: {e}")
            raise

    async def fetch_bilateral_contracts(
            self,
            start_date: date,
            end_date: date
    ) -> pd.DataFrame:
        """
        Fetch bilateral contracts data

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with bilateral contracts
        """
        request = BilateralContractsRequest(
            startDate=datetime.combine(start_date, datetime.min.time()),
            endDate=datetime.combine(end_date, datetime.max.time())
        )

        try:
            # Fetch both buy and sell data
            buy_task = self.client.get_paginated(
                APIEndpoints.BILATERAL_CONTRACTS_BID,
                request.dict()
            )
            sell_task = self.client.get_paginated(
                APIEndpoints.BILATERAL_CONTRACTS_OFFER,
                request.dict()
            )

            buy_data, sell_data = await asyncio.gather(buy_task, sell_task)

            df = self.processor.process_bilateral_contracts(buy_data, sell_data)
            logger.info(f"Fetched bilateral contracts: {len(df)} records")
            return df

        except APIError as e:
            logger.error(f"Failed to fetch bilateral contracts: {e}")
            raise

    # Generation Data fetchers
    async def fetch_generation_data(
            self,
            organization_id: int,
            start_date: date,
            end_date: date,
            power_plant_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch generation data for an organization

        Args:
            organization_id: Organization ID
            start_date: Start date
            end_date: End date
            power_plant_id: Optional power plant ID filter

        Returns:
            DataFrame with generation data
        """
        request = GenerationDataRequest(
            organizationId=organization_id,
            startDate=datetime.combine(start_date, datetime.min.time()),
            endDate=datetime.combine(end_date, datetime.max.time()),
            powerPlantId=power_plant_id
        )

        try:
            data = await self.client.get_paginated(
                APIEndpoints.GENERATION_REALTIME,
                request.dict()
            )

            df = self.processor.process_generation_data(data)
            logger.info(f"Fetched generation data for org {organization_id}: {len(df)} records")
            return df

        except APIError as e:
            logger.error(f"Failed to fetch generation data: {e}")
            raise

    async def fetch_kgup_data(
            self,
            organization_id: int,
            start_date: date,
            end_date: date
    ) -> pd.DataFrame:
        """
        Fetch KGÜP (Kesinleşmiş Günlük Üretim Planı) data

        Args:
            organization_id: Organization ID
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with KGÜP data
        """
        request = OrganizationRequest(
            organizationId=organization_id,
            startDate=datetime.combine(start_date, datetime.min.time()),
            endDate=datetime.combine(end_date, datetime.max.time())
        )

        try:
            data = await self.client.get_paginated(
                APIEndpoints.GENERATION_DPP,
                request.dict()
            )

            df = self.processor.process_kgup_data(data)
            logger.info(f"Fetched KGÜP data for org {organization_id}: {len(df)} records")
            return df

        except APIError as e:
            logger.error(f"Failed to fetch KGÜP data: {e}")
            raise

    # Dashboard Data fetchers
    async def fetch_dashboard_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch all dashboard data

        Returns:
            Dictionary of DataFrames for each dashboard metric
        """
        endpoints = [
            ("bpm", APIEndpoints.DASHBOARD_BPM),
            ("dam", APIEndpoints.DASHBOARD_DAM),
            ("idm", APIEndpoints.DASHBOARD_IDM),
            ("consumption", APIEndpoints.DASHBOARD_CONSUMPTION),
            ("generation", APIEndpoints.DASHBOARD_GENERATION),
            ("weighted_price", APIEndpoints.DASHBOARD_WEIGHTED_PRICE)
        ]

        tasks = []
        for name, endpoint in endpoints:
            tasks.append(self.client.get(endpoint))

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            dashboard_data = {}
            for (name, _), result in zip(endpoints, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch {name} dashboard: {result}")
                    dashboard_data[name] = pd.DataFrame()
                else:
                    dashboard_data[name] = self.processor.process_dashboard_data(result)

            return dashboard_data

        except Exception as e:
            logger.error(f"Failed to fetch dashboard data: {e}")
            raise

    # Consumption Data fetchers
    async def fetch_consumption_data(
            self,
            start_date: date,
            end_date: date,
            province_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch consumption data

        Args:
            start_date: Start date
            end_date: End date
            province_id: Optional province filter

        Returns:
            DataFrame with consumption data
        """
        request = ConsumptionDataRequest(
            startDate=datetime.combine(start_date, datetime.min.time()),
            endDate=datetime.combine(end_date, datetime.max.time()),
            provinceId=province_id
        )

        try:
            data = await self.client.get_paginated(
                APIEndpoints.CONSUMPTION_QUANTITY,
                request.dict()
            )

            df = self.processor.process_consumption_data(data)
            logger.info(f"Fetched consumption data: {len(df)} records")
            return df

        except APIError as e:
            logger.error(f"Failed to fetch consumption data: {e}")
            raise

    # Combined data fetchers
    async def fetch_organization_overview(
            self,
            organization_id: int,
            start_date: date,
            end_date: date
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch complete overview data for an organization

        Args:
            organization_id: Organization ID
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary containing:
            - uevcb_list: List of UEVCBs
            - generation: Generation data
            - kgup: KGÜP data
            - market_data: Market participation data
        """
        tasks = {
            "uevcb_list": self.fetch_uevcb_list(organization_id),
            "generation": self.fetch_generation_data(organization_id, start_date, end_date),
            "kgup": self.fetch_kgup_data(organization_id, start_date, end_date),
            "ptf": self.fetch_ptf_data(start_date, end_date),
            "smf": self.fetch_smf_data(start_date, end_date)
        }

        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                logger.error(f"Failed to fetch {name} for org {organization_id}: {e}")
                results[name] = pd.DataFrame() if name != "uevcb_list" else []

        return results