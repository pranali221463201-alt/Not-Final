# route_optimization/router.py

from fastapi import APIRouter
from route_optimization.schemas import (
    CustomerOrderRequest,
    RouteOptimizationResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ro",
    tags=["Route Optimization"]
)


@router.get("/health")
def health_check():
    return {
        "status": "success",
        "module": "Route Optimization",
        "message": "RO module is running"
    }

try:
    from route_optimization.service import ro_service
    SERVICE_AVAILABLE = True
except Exception as e:
    logger.error(f"Failed to load route optimization service: {e}")
    SERVICE_AVAILABLE = False
    ro_service = None

@router.get("/run/{order_id}")
def run_route_optimization(order_id: str):
    if not SERVICE_AVAILABLE:
        return {"status": "ERROR", "message": "Route optimization service not available"}
    try:
        return ro_service.run_optimization(order_id)
    except Exception as e:
        logger.error(f"Error in run_route_optimization: {e}")
        return {"status": "ERROR", "message": str(e)}

@router.get("/plan/{order_id}")
def get_fulfillment_plan(order_id: str):
    if not SERVICE_AVAILABLE:
        return {"status": "ERROR", "message": "Route optimization service not available"}
    try:
        return ro_service.get_fulfillment_plan(order_id)
    except Exception as e:
        logger.error(f"Error in get_fulfillment_plan: {e}")
        return {"status": "ERROR", "message": str(e)}

@router.get("/kpis/{order_id}")
def get_ro_kpis(order_id: str):
    if not SERVICE_AVAILABLE:
        return {"status": "ERROR", "message": "Route optimization service not available"}
    try:
        return ro_service.get_order_kpis(order_id)
    except Exception as e:
        logger.error(f"Error in get_ro_kpis: {e}")
        return {"status": "ERROR", "message": str(e)}

@router.get("/history")
def get_ro_history():
    if not SERVICE_AVAILABLE:
        return {"orders": []}
    try:
        return ro_service.get_order_history()
    except Exception as e:
        logger.error(f"Error in get_ro_history: {e}")
        return {"orders": []}

@router.get("/explain/{order_id}")
def explain_ro_decision(order_id: str):
    if not SERVICE_AVAILABLE:
        return {"status": "ERROR", "message": "Route optimization service not available"}
    try:
        return ro_service.explain_order_decision(order_id)
    except Exception as e:
        logger.error(f"Error in explain_ro_decision: {e}")
        return {"status": "ERROR", "message": str(e)}

@router.get("/chart-data/{order_id}")
def get_chart_data(order_id: str):
    if not SERVICE_AVAILABLE:
        return {"status": "ERROR", "message": "Route optimization service not available"}
    try:
        return ro_service.get_chart_data(order_id)
    except Exception as e:
        logger.error(f"Error in get_chart_data: {e}")
        return {"status": "ERROR", "message": str(e)}

@router.get("/dashboard-summary")
def get_dashboard_summary():
    if not SERVICE_AVAILABLE:
        return {
            "total_orders": 0,
            "fully_fulfilled": 0,
            "partially_fulfilled": 0,
            "infeasible_orders": 0,
            "average_fulfillment_rate": 0,
        }
    try:
        return ro_service.get_dashboard_summary()
    except Exception as e:
        logger.error(f"Error in get_dashboard_summary: {e}")
        return {
            "total_orders": 0,
            "fully_fulfilled": 0,
            "partially_fulfilled": 0,
            "infeasible_orders": 0,
            "average_fulfillment_rate": 0,
        }