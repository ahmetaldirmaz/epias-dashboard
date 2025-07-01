"""
Data models for EPİAŞ API responses
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class PageSort(BaseModel):
    """Page sort configuration"""
    direction: str = "ASC"  # ASC or DESC
    field: str = "date"


class PageConfig(BaseModel):
    """Pagination configuration"""
    number: int = 1
    size: int = 100
    sort: Optional[PageSort] = None
    total: Optional[int] = None


class BaseRequest(BaseModel):
    """Base request model with pagination"""
    page: Optional[PageConfig] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S%z"),
            date: lambda v: v.strftime("%Y-%m-%d")
        }


class DateRangeRequest(BaseRequest):
    """Request with date range"""
    startDate: datetime
    endDate: datetime

    @validator("endDate")
    def validate_date_range(cls, v, values):
        if "startDate" in values and v < values["startDate"]:
            raise ValueError("endDate must be after startDate")
        return v


class OrganizationRequest(DateRangeRequest):
    """Request with organization ID"""
    organizationId: int


class PowerPlant(BaseModel):
    """Power plant model"""
    id: int
    name: str
    eic: Optional[str] = None
    shortName: Optional[str] = None
    status: Optional[str] = None


class Organization(BaseModel):
    """Organization model"""
    id: int
    name: str
    eic: Optional[str] = None
    status: Optional[str] = None


class UEVCB(BaseModel):
    """UEVCB (Uzlaştırmaya Esas Veriş-Çekiş Birimi) model"""
    id: int
    name: str
    eic: str
    organizationId: int
    organizationName: Optional[str] = None


class MarketData(BaseModel):
    """Base market data model"""
    date: datetime
    value: float

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PTFData(MarketData):
    """PTF (Piyasa Takas Fiyatı) data"""
    price: float = Field(alias="value")
    hour: Optional[int] = None


class GenerationData(BaseModel):
    """Generation data model"""
    date: datetime
    powerPlantId: Optional[int] = None
    powerPlantName: Optional[str] = None
    uevcbId: Optional[int] = None
    uevcbName: Optional[str] = None
    generationType: Optional[str] = None
    value: float
    unit: str = "MWh"


class BilateralContractData(BaseModel):
    """Bilateral contract data"""
    date: datetime
    contractType: str
    quantity: float
    unit: str = "MWh"


class ConsumptionData(BaseModel):
    """Consumption data model"""
    date: datetime
    province: Optional[str] = None
    district: Optional[str] = None
    profileGroup: Optional[str] = None
    subscriberType: Optional[str] = None
    value: float
    unit: str = "MWh"


class ImbalanceData(BaseModel):
    """Imbalance data model"""
    date: datetime
    hour: int
    direction: str  # "Pozitif" or "Negatif"
    quantity: Optional[float] = None
    amount: Optional[float] = None


class DashboardData(BaseModel):
    """Dashboard summary data"""
    lastUpdate: datetime
    metric: str
    value: float
    change: Optional[float] = None
    changePercent: Optional[float] = None


# Request models for specific endpoints
class OrganizationListRequest(DateRangeRequest):
    """Request for organization list"""
    pass


class PowerPlantListRequest(DateRangeRequest):
    """Request for power plant list"""
    pass


class UEVCBListRequest(BaseRequest):
    """Request for UEVCB list"""
    organizationId: int


class GenerationDataRequest(OrganizationRequest):
    """Request for generation data"""
    powerPlantId: Optional[int] = None
    uevcbId: Optional[int] = None


class MarketDataRequest(DateRangeRequest):
    """Request for market data"""
    period: Optional[str] = None  # "HOURLY", "DAILY", "MONTHLY"


class BilateralContractsRequest(DateRangeRequest):
    """Request for bilateral contracts"""
    contractType: Optional[str] = None


class ConsumptionDataRequest(DateRangeRequest):
    """Request for consumption data"""
    provinceId: Optional[int] = None
    districtId: Optional[int] = None
    profileGroup: Optional[str] = None


# Response models
class APIResponse(BaseModel):
    """Base API response"""
    body: Dict[str, Any]
    resultCode: str
    resultDescription: str

    @property
    def is_success(self) -> bool:
        return self.resultCode == "200"

    @property
    def content(self) -> Any:
        return self.body.get("content", [])

    @property
    def page_info(self) -> Optional[PageConfig]:
        if "page" in self.body:
            return PageConfig(**self.body["page"])
        return None


class DataResponse(BaseModel):
    """Generic data response wrapper"""
    items: List[Dict[str, Any]]
    page: Optional[PageConfig] = None
    total: Optional[int] = None
    statistics: Optional[Dict[str, Any]] = None


# Enums for common values
class SystemDirection(str, Enum):
    """System direction (Sistem Yönü)"""
    SURPLUS = "Enerji Fazlası"  # Energy surplus
    DEFICIT = "Enerji Açığı"  # Energy deficit
    BALANCED = "Dengede"  # Balanced


class ContractType(str, Enum):
    """Bilateral contract types"""
    EUAS_GTS = "EÜAŞ-GTŞ"
    OTHER = "Diğer"


class GenerationType(str, Enum):
    """Generation types"""
    WIND = "Rüzgar"
    SOLAR = "Güneş"
    HYDRO_DAM = "Barajlı"
    HYDRO_RUN = "Akarsu"
    NATURAL_GAS = "Doğal Gaz"
    COAL_LIGNITE = "Linyit"
    COAL_IMPORT = "İthal Kömür"
    NUCLEAR = "Nükleer"
    GEOTHERMAL = "Jeotermal"
    BIOMASS = "Biyokütle"
    OTHER = "Diğer"