from typing import Dict, Optional, Union, List
import math
from pydantic import BaseModel
from litestar import Router, Request, post
from litestar.exceptions import ValidationException

class PriceRequest(BaseModel):
    """Request model for pharmacy price calculations."""
    prices: Dict[str, float]

class PriceResponse(BaseModel):
    """Response model for pharmacy price calculations."""
    delivery_costs: Dict[str, float]
    
    class Config:
        """Configure Pydantic to handle NaN values properly."""
        json_encoders = {
            float: lambda v: None if math.isnan(v) else v
        }

def calculate_apollo_charges(price: float) -> float:
    """Calculate hidden charges for Apollo Pharmacy."""
    if price < 1:
        raise ValidationException("Price must be at least 1")
    
    if price < 150:
        hidden_cost = 99
    elif price < 250:
        hidden_cost = 79
    elif price < 300:
        hidden_cost = 29  
    else:
        hidden_cost = 0 
    
    platform_cost = 4
    handling_cost = 6
    
    return hidden_cost + platform_cost + handling_cost

def calculate_kauverymeds_charges(price: float) -> float:
    """Calculate hidden charges for Kauvery Meds."""
    if price < 1:
        raise ValidationException("Price must be at least 1")
    return 75

def calculate_medkart_charges(price: float) -> float:

    if price < 1:
        raise ValidationException("Price must be at least 1")
    
    return 59

def calculate_mrmed_charges(price: float) -> float:
    """Calculate hidden charges for MR Med."""
    if price < 1:
        raise ValidationException("Price must be at least 1")
    
    if price <= 1500:
        hidden_cost = 89
    elif price < 1700:
        hidden_cost = 59
    elif price < 2000:
        hidden_cost = 39
    else:
        hidden_cost = 0 
    
    return hidden_cost

def calculate_netmeds_charges(price: float) -> float:
    """Calculate hidden charges for Netmeds."""
    if price < 1:
        raise ValidationException("Price must be at least 1")

    if price <= 250:
        hidden_cost = 69
    elif price <= 350:
        hidden_cost = 49
    else:
        hidden_cost = 0  
    
    return hidden_cost

def calculate_pharmeasy_charges(price: float) -> float:
    """Calculate hidden charges for PharmEasy."""
    if price < 1:
        raise ValidationException("Price must be at least 1")
    
    if price < 300:
        hidden_cost = 99  
    elif price < 350:
        hidden_cost = 75
    else:
        hidden_cost = 0 
    
    platform_cost = 7
    return hidden_cost + platform_cost

def calculate_tata1mg_charges(price: float) -> float:
    """Calculate hidden charges for Tata 1mg."""
    if price < 1:
        raise ValidationException("Price must be at least 1")
    
    if price < 100:
        hidden_cost = 79
    elif price < 200:
        hidden_cost = 75
    else:
        hidden_cost = 0  
    
    platform_cost = 4
    return hidden_cost + platform_cost

def calculate_truemeds_charges(price: float) -> float:
    """Calculate hidden charges for Truemeds."""
    if price < 1:
        raise ValidationException("Price must be at least 1")
    
    if price < 400:
        hidden_cost = 39
    elif price < 500:
        hidden_cost = 29
    else:
        hidden_cost = 0  

    return hidden_cost

def calculate_wellnessforever_charges(price: float) -> float:
    """Calculate hidden charges for Wellness Forever."""
    if price < 1:
        raise ValidationException("Price must be at least 1")
    if price < 1000:
        hidden_cost = 50
    else:
        hidden_cost = 0
    return hidden_cost

@post("/cost")
async def calculate_delivery_costs(request: Request, data: PriceRequest) -> PriceResponse:
    """
    Calculate delivery costs for all provided pharmacies.
    
    Input format: {"pharmacy_name": mrp, ...}
    Output format: {"delivery_costs": {"pharmacy_name": delivery_cost, ...}}
    """
    request.logger.info("Path: /cost: Processing pharmacy delivery costs")
    
    delivery_costs = {}
    calculation_functions = {
        "apollopharmacy": calculate_apollo_charges,
        "kauverymeds": calculate_kauverymeds_charges,
        "medkart": calculate_medkart_charges,
        "mrmed": calculate_mrmed_charges,
        "netmeds": calculate_netmeds_charges,
        "pharmeasy": calculate_pharmeasy_charges,
        "tata1mg": calculate_tata1mg_charges, 
        "truemeds": calculate_truemeds_charges,
        "wellnessforever": calculate_wellnessforever_charges
    }
    
    for pharmacy, price in data.prices.items():
        try:
            if pharmacy in calculation_functions:
                try:
                    delivery_costs[pharmacy] = calculation_functions[pharmacy](price)
                except ValidationException as e:
                    # For validation errors, return NaN
                    request.logger.warning(f"Validation error for {pharmacy}: {str(e)}")
                    delivery_costs[pharmacy] = float('nan')
                except Exception as e:
                    # For any other errors, return NaN and log the error
                    request.logger.error(f"Error calculating for {pharmacy}: {str(e)}")
                    delivery_costs[pharmacy] = float('nan')
            else:
                # Source not available
                request.logger.warning(f"Unknown pharmacy source: {pharmacy}")
                delivery_costs[pharmacy] = float('nan')
        except Exception as e:
            # Catch any other unexpected errors
            request.logger.error(f"Unexpected error processing {pharmacy}: {str(e)}")
            delivery_costs[pharmacy] = float('nan')
    
    return PriceResponse(delivery_costs=delivery_costs)

# Create the router with a single endpoint
cost_router = Router(
    path="/",
    route_handlers=[calculate_delivery_costs]
)

from litestar import Litestar
from litestar.logging import LoggingConfig

# Configure logging
logging_config = LoggingConfig(
    loggers={
        "app": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }
)


app = Litestar(
    route_handlers=[cost_router],
    logging_config=logging_config,
    debug=True
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)