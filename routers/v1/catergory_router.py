from fastapi import APIRouter
from fastapi import status
from typing import Optional
from helper.is_site_available import check_if_site_available
from helper.error_messages import error_handler
from opentelemetry import trace
from opentelemetry.metrics import get_meter

tracer = trace.get_tracer(__name__)
meter = get_meter(__name__)
request_counter = meter.create_counter(
    "category_requests",
    description="Number of category requests",
)
empty_result_counter = meter.create_counter(
    "empty_category_results",
    description="Number of empty category results",
)

router = APIRouter(tags=["Category Torrents Route"])


@router.get("/")
@router.get("")
async def get_category(
    site: str,
    query: str,
    category: str,
    limit: Optional[int] = 0,
    page: Optional[int] = 1,
):
    with tracer.start_as_current_span("get_category") as span:
        span.set_attribute("site", site)
        span.set_attribute("query", query)
        span.set_attribute("category", category)
        span.set_attribute("limit", limit)
        span.set_attribute("page", page)

        request_counter.add(1, {"site": site, "status": "requested"})

        site = site.lower()
        query = query.lower()
        category = category.lower()
        all_sites = check_if_site_available(site)
        if all_sites:
            limit = (
                all_sites[site]["limit"]
                if limit == 0 or limit > all_sites[site]["limit"]
                else limit
            )

            if all_sites[site]["search_by_category"]:
                if category not in all_sites[site]["categories"]:
                    span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Category not available"))
                    request_counter.add(1, {"site": site, "status": "category_not_available"})
                    return error_handler(
                        status_code=status.HTTP_404_NOT_FOUND,
                        json_message={
                            "error": "Selected category not available.",
                            "available_categories": all_sites[site]["categories"],
                        },
                    )
                resp = await all_sites[site]["website"]().search_by_category(
                    query, category, page, limit
                )
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
                span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Category search not available"))
                request_counter.add(1, {"site": site, "status": "category_search_not_available"})
                return error_handler(
                    status_code=status.HTTP_404_NOT_FOUND,
                    json_message={
                        "error": "Category search not available for {}.".format(site)
                    },
                )
        span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Selected Site Not Available"))
        request_counter.add(1, {"site": site, "status": "not_available"})
        return error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            json_message={"error": "Selected Site Not Available"},
        )