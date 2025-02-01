from fastapi import APIRouter, status
from typing import Optional
from helper.is_site_available import check_if_site_available
from helper.error_messages import error_handler
from opentelemetry import trace
from opentelemetry.metrics import get_meter

tracer = trace.get_tracer(__name__)
meter = get_meter(__name__)
request_counter = meter.create_counter(
    "trending_requests",
    description="Number of trending requests",
)
empty_result_counter = meter.create_counter(
    "empty_trending_results",
    description="Number of empty trending results",
)

router = APIRouter(tags=["Trending Torrents"])


@router.get("/")
@router.get("")
async def get_trending(
    site: str,
    limit: Optional[int] = 0,
    category: Optional[str] = None,
    page: Optional[int] = 1,
):
    with tracer.start_as_current_span("get_trending") as span:
        span.set_attribute("site", site)
        span.set_attribute("limit", limit)
        span.set_attribute("category", category)
        span.set_attribute("page", page)

        request_counter.add(1, {"site": site, "status": "requested"})

        site = site.lower()
        all_sites = check_if_site_available(site)
        category = category.lower() if category is not None else None
        if all_sites:
            limit = (
                all_sites[site]["limit"]
                if limit == 0 or limit > all_sites[site]["limit"]
                else limit
            )
            if all_sites[site]["trending_available"]:
                if not category is None and not all_sites[site]["trending_category"]:
                    span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Category not available"))
                    request_counter.add(1, {"site": site, "status": "category_not_available"})
                    return error_handler(
                        status_code=status.HTTP_404_NOT_FOUND,
                        json_message={
                            "error": "Search by trending category not available for {}.".format(
                                site
                            )
                        },
                    )
                if not category is None and category not in all_sites[site]["categories"]:
                    span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Category not available"))
                    request_counter.add(1, {"site": site, "status": "category_not_available"})
                    return error_handler(
                        status_code=status.HTTP_404_NOT_FOUND,
                        json_message={
                            "error": "Selected category not available.",
                            "available_categories": all_sites[site]["categories"],
                        },
                    )
                resp = await all_sites[site]["website"]().trending(category, page, limit)
                if resp is None:
                    span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Site Blocked"))
                    request_counter.add(1, {"site": site, "status": "blocked"})
                    return error_handler(
                        status_code=status.HTTP_403_FORBIDDEN,
                        json_message={
                            "error": "Website Blocked Change IP or Website Domain."
                        },
                    )
                elif len(resp["data"]) > 0:
                    request_counter.add(1, {"site": site, "status": "success"})
                    return resp
                else:
                    span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Result not found"))
                    request_counter.add(1, {"site": site, "status": "empty"})
                    empty_result_counter.add(1, {"site": site})
                    return error_handler(
                        status_code=status.HTTP_404_NOT_FOUND,
                        json_message={"error": "Result not found."},
                    )
            else:
                span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Trending search not available"))
                request_counter.add(1, {"site": site, "status": "trending_search_not_available"})
                return error_handler(
                    status_code=status.HTTP_404_NOT_FOUND,
                    json_message={
                        "error": "Trending search not available for {}.".format(site)
                    },
                )
        span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Selected Site Not Available"))
        request_counter.add(1, {"site": site, "status": "not_available"})
        return error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            json_message={"error": "Selected Site Not Available"},
        )