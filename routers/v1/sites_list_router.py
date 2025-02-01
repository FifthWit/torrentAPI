from fastapi import APIRouter, status
from helper.is_site_available import check_if_site_available, sites_config
from helper.error_messages import error_handler
from opentelemetry import trace
from opentelemetry.metrics import get_meter

tracer = trace.get_tracer(__name__)
meter = get_meter(__name__)
request_counter = meter.create_counter(
    "sites_list_requests",
    description="Number of sites list requests",
)

router = APIRouter(tags=["Get all sites"])


@router.get("/")
@router.get("")
async def get_all_supported_sites():
    with tracer.start_as_current_span("get_all_supported_sites") as span:
        request_counter.add(1, {"status": "requested"})

        all_sites = check_if_site_available("1337x")
        sites_list = [site for site in all_sites.keys() if all_sites[site]["website"]]
        
        request_counter.add(1, {"status": "success"})
        return error_handler(
            status_code=status.HTTP_200_OK,
            json_message={
                "supported_sites": sites_list,
            },
        )


@router.get("/config")
async def get_site_config():
    with tracer.start_as_current_span("get_site_config") as span:
        request_counter.add(1, {"status": "requested"})

        request_counter.add(1, {"status": "success"})
        return error_handler(
            status_code=status.HTTP_200_OK,
            json_message=sites_config
        )