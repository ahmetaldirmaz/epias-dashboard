"""
EPİAŞ API endpoint definitions
"""
from enum import Enum


class APIEndpoints(str, Enum):
    """API endpoint paths"""

    # Dashboard endpoints
    DASHBOARD_BPM = "/dashboard/balancing-power-market"
    DASHBOARD_DAM = "/dashboard/day-ahead-market"
    DASHBOARD_IDM = "/dashboard/intra-day-market"
    DASHBOARD_MMS = "/dashboard/market-message-system"
    DASHBOARD_CONSUMPTION = "/dashboard/realtime-consumption"
    DASHBOARD_GENERATION = "/dashboard/realtime-generation"
    DASHBOARD_WEIGHTED_PRICE = "/dashboard/weighted-average-price"

    # Generation data endpoints
    GENERATION_AIC = "/generation/data/aic"  # Emre Amade Kapasite
    GENERATION_DPP = "/generation/data/dpp"  # Kesinleşmiş Günlük Üretim Planı
    GENERATION_INJECTION = "/generation/data/injection-quantity"  # UEVM
    GENERATION_REALTIME = "/generation/data/realtime-generation"
    GENERATION_ORG_LIST = "/generation/data/organization-list"
    GENERATION_POWERPLANT_LIST = "/generation/data/powerplant-list"
    GENERATION_REGION_LIST = "/generation/data/region-list"
    GENERATION_UEVCB_LIST = "/generation/data/uevcb-list"

    # Market data endpoints - Bilateral Contracts
    BILATERAL_CONTRACTS_AMOUNT = "/markets/bilateral-contracts/data/amount-of-bilateral-contracts"
    BILATERAL_CONTRACTS_BID = "/markets/bilateral-contracts/data/bilateral-contracts-bid-quantity"
    BILATERAL_CONTRACTS_OFFER = "/markets/bilateral-contracts/data/bilateral-contracts-offer-quantity"

    # Market data endpoints - Balancing Power Market (BPM)
    BPM_ORDER_SUMMARY_UP = "/markets/bpm/data/order-summary-up"  # YAL
    BPM_ORDER_SUMMARY_DOWN = "/markets/bpm/data/order-summary-down"  # YAT
    BPM_SYSTEM_DIRECTION = "/markets/bpm/data/system-direction"
    BPM_SYSTEM_MARGINAL_PRICE = "/markets/bpm/data/system-marginal-price"

    # Market data endpoints - Day Ahead Market (DAM/GÖP)
    DAM_BLOCK_BID = "/markets/dam/data/amount-of-block-buying"
    DAM_BLOCK_OFFER = "/markets/dam/data/amount-of-block-selling"
    DAM_CLEARING_QUANTITY = "/markets/dam/data/clearing-quantity"
    DAM_CLEARING_ORG_LIST = "/markets/dam/data/clearing-quantity-organization-list"
    DAM_TRADE_VOLUME = "/markets/dam/data/day-ahead-market-trade-volume"
    DAM_FLEXIBLE_BID = "/markets/dam/data/flexible-offer-buying-quantity"
    DAM_FLEXIBLE_OFFER = "/markets/dam/data/flexible-offer-selling-quantity"
    DAM_INTERIM_MCP = "/markets/dam/data/interim-mcp"  # Kesinleşmemiş PTF
    DAM_MCP = "/markets/dam/data/mcp"  # PTF
    DAM_SUBMITTED_BID = "/markets/dam/data/submitted-bid-order-volume"
    DAM_SUBMITTED_OFFER = "/markets/dam/data/submitted-sales-order-volume"
    DAM_SUPPLY_DEMAND = "/markets/dam/data/supply-demand"

    # Market data endpoints - Intraday Market (IDM/GİP)
    IDM_BID_OFFER = "/markets/idm/data/bid-offer-quantities"
    IDM_MATCHING_QUANTITY = "/markets/idm/data/matching-quantity"
    IDM_MIN_MAX_BID = "/markets/idm/data/min-max-bid-price"
    IDM_MIN_MAX_MATCH = "/markets/idm/data/min-max-matching-price"
    IDM_MIN_MAX_OFFER = "/markets/idm/data/min-max-offer-price"
    IDM_TRADE_VOLUME = "/markets/idm/data/intraday-trade-volume"
    IDM_WEIGHTED_AVERAGE = "/markets/idm/data/weighted-average-price"

    # Consumption data endpoints
    CONSUMPTION_QUANTITY = "/consumption/data/consumption-quantity"
    CONSUMPTION_CONSUMER_QUANTITY = "/consumption/data/consumer-quantity"
    CONSUMPTION_DEMAND_FORECAST = "/consumption/data/demand-forecast"
    CONSUMPTION_DISTRIBUTION_REGION = "/consumption/data/distribution-region"
    CONSUMPTION_ELIGIBLE_CONSUMER_COUNT = "/consumption/data/eligible-consumer-count"
    CONSUMPTION_ELIGIBLE_CONSUMER_QUANTITY = "/consumption/data/eligible-consumer-quantity"
    CONSUMPTION_LOAD_ESTIMATION_PLAN = "/consumption/data/load-estimation-plan"
    CONSUMPTION_REALTIME = "/consumption/data/realtime-consumption"
    CONSUMPTION_WITHDRAWAL_QUANTITY = "/consumption/data/st-uecm"  # Serbest Tüketici UEÇM

    # Main data endpoints
    MAIN_DATE_INIT = "/main/date-init"
    MAIN_PROVINCE_LIST = "/main/province-list"
    MAIN_DISTRICT_LIST = "/main/district-list"

    # Ancillary services
    ANCILLARY_PRIMARY_CAPACITY_AMOUNT = "/markets/ancillary-services/data/primary-frequency-capacity-amount"
    ANCILLARY_PRIMARY_CAPACITY_PRICE = "/markets/ancillary-services/data/primary-frequency-capacity-price"
    ANCILLARY_SECONDARY_CAPACITY_AMOUNT = "/markets/ancillary-services/data/secondary-frequency-capacity-amount"
    ANCILLARY_SECONDARY_CAPACITY_PRICE = "/markets/ancillary-services/data/secondary-frequency-capacity-price"

    # Imbalance
    IMBALANCE_QUANTITY = "/markets/imbalance/data/imbalance-quantity"
    IMBALANCE_AMOUNT = "/markets/imbalance/data/imbalance-amount"

    # Export endpoints (append 'export' to path)
    def get_export_endpoint(self) -> str:
        """Convert data endpoint to export endpoint"""
        return self.value.replace("/data/", "/export/")


class RequestMethod(str, Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"


# Endpoint configurations
ENDPOINT_CONFIGS = {
    # GET endpoints
    APIEndpoints.DASHBOARD_BPM: RequestMethod.GET,
    APIEndpoints.DASHBOARD_DAM: RequestMethod.GET,
    APIEndpoints.DASHBOARD_IDM: RequestMethod.GET,
    APIEndpoints.DASHBOARD_MMS: RequestMethod.GET,
    APIEndpoints.DASHBOARD_CONSUMPTION: RequestMethod.GET,
    APIEndpoints.DASHBOARD_GENERATION: RequestMethod.GET,
    APIEndpoints.DASHBOARD_WEIGHTED_PRICE: RequestMethod.GET,
    APIEndpoints.GENERATION_POWERPLANT_LIST: RequestMethod.GET,
    APIEndpoints.GENERATION_REGION_LIST: RequestMethod.GET,
    APIEndpoints.CONSUMPTION_DISTRIBUTION_REGION: RequestMethod.GET,
    APIEndpoints.MAIN_DATE_INIT: RequestMethod.GET,
    APIEndpoints.MAIN_PROVINCE_LIST: RequestMethod.GET,

    # POST endpoints (most are POST)
    APIEndpoints.GENERATION_AIC: RequestMethod.POST,
    APIEndpoints.GENERATION_DPP: RequestMethod.POST,
    APIEndpoints.GENERATION_INJECTION: RequestMethod.POST,
    APIEndpoints.GENERATION_REALTIME: RequestMethod.POST,
    APIEndpoints.GENERATION_ORG_LIST: RequestMethod.POST,
    APIEndpoints.GENERATION_UEVCB_LIST: RequestMethod.POST,
    APIEndpoints.BILATERAL_CONTRACTS_AMOUNT: RequestMethod.POST,
    APIEndpoints.BILATERAL_CONTRACTS_BID: RequestMethod.POST,
    APIEndpoints.BILATERAL_CONTRACTS_OFFER: RequestMethod.POST,
    APIEndpoints.BPM_ORDER_SUMMARY_UP: RequestMethod.POST,
    APIEndpoints.BPM_ORDER_SUMMARY_DOWN: RequestMethod.POST,
    APIEndpoints.BPM_SYSTEM_DIRECTION: RequestMethod.POST,
    APIEndpoints.BPM_SYSTEM_MARGINAL_PRICE: RequestMethod.POST,
    APIEndpoints.DAM_BLOCK_BID: RequestMethod.POST,
    APIEndpoints.DAM_BLOCK_OFFER: RequestMethod.POST,
    APIEndpoints.DAM_CLEARING_QUANTITY: RequestMethod.POST,
    APIEndpoints.DAM_CLEARING_ORG_LIST: RequestMethod.POST,
    APIEndpoints.DAM_TRADE_VOLUME: RequestMethod.POST,
    APIEndpoints.DAM_FLEXIBLE_BID: RequestMethod.POST,
    APIEndpoints.DAM_FLEXIBLE_OFFER: RequestMethod.POST,
    APIEndpoints.DAM_INTERIM_MCP: RequestMethod.POST,
    APIEndpoints.DAM_MCP: RequestMethod.POST,
    APIEndpoints.DAM_SUBMITTED_BID: RequestMethod.POST,
    APIEndpoints.DAM_SUBMITTED_OFFER: RequestMethod.POST,
    APIEndpoints.DAM_SUPPLY_DEMAND: RequestMethod.POST,
    APIEndpoints.IDM_BID_OFFER: RequestMethod.POST,
    APIEndpoints.IDM_MATCHING_QUANTITY: RequestMethod.POST,
    APIEndpoints.IDM_MIN_MAX_BID: RequestMethod.POST,
    APIEndpoints.IDM_MIN_MAX_MATCH: RequestMethod.POST,
    APIEndpoints.IDM_MIN_MAX_OFFER: RequestMethod.POST,
    APIEndpoints.IDM_TRADE_VOLUME: RequestMethod.POST,
    APIEndpoints.IDM_WEIGHTED_AVERAGE: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_QUANTITY: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_CONSUMER_QUANTITY: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_DEMAND_FORECAST: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_ELIGIBLE_CONSUMER_COUNT: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_ELIGIBLE_CONSUMER_QUANTITY: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_LOAD_ESTIMATION_PLAN: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_REALTIME: RequestMethod.POST,
    APIEndpoints.CONSUMPTION_WITHDRAWAL_QUANTITY: RequestMethod.POST,
    APIEndpoints.MAIN_DISTRICT_LIST: RequestMethod.POST,
    APIEndpoints.ANCILLARY_PRIMARY_CAPACITY_AMOUNT: RequestMethod.POST,
    APIEndpoints.ANCILLARY_PRIMARY_CAPACITY_PRICE: RequestMethod.POST,
    APIEndpoints.ANCILLARY_SECONDARY_CAPACITY_AMOUNT: RequestMethod.POST,
    APIEndpoints.ANCILLARY_SECONDARY_CAPACITY_PRICE: RequestMethod.POST,
    APIEndpoints.IMBALANCE_QUANTITY: RequestMethod.POST,
    APIEndpoints.IMBALANCE_AMOUNT: RequestMethod.POST,
}