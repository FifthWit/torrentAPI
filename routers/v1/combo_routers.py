from fastapi import APIRouter, status
from typing import Optional
from helper.is_site_available import check_if_site_available
import time
import asyncio
from helper.error_messages import error_handler
from opentelemetry import trace
from opentelemetry.metrics import get_meter

tracer = trace.get_tracer(__name__)
meter = get_meter(__name__)
request_counter = meter.create_counter(
    "combo_requests",
    description="Number of combo requests",
)
empty_result_counter = meter.create_counter(
    "empty_combo_results",
    description="Number of empty combo results",
)

router = APIRouter(tags=["Combo Routes"])


@router.get("/search")
async def get_search_combo(query: str, limit: Optional[int] = 0):
    with tracer.start_as_current_span("get_search_combo") as span:
        span.set_attribute("query", query)
        span.set_attribute("limit", limit)

        request_counter.add(1, {"status": "requested"})

        start_time = time.time()
        query = query.lower()
        all_sites = check_if_site_available("1337x")
        sites_list = list(all_sites.keys())
        tasks = []
        COMBO = {"data": []}
        total_torrents_overall = 0
        for site in sites_list:
            limit = (
                all_sites[site]["limit"]
                if limit == 0 or limit > all_sites[site]["limit"]
                else limit
            )
            tasks.append(
                asyncio.create_task(
                    all_sites[site]["website"]().search(query, page=1, limit=limit)
                )
            )
        results = await asyncio.gather(*tasks)
        for res in results:
            if res is not None and len(res["data"]) > 0:
                for torrent in res["data"]:
                    COMBO["data"].append(torrent)
                total_torrents_overall = total_torrents_overall + res["total"]
            else:
                empty_result_counter.add(1, {"site": site})
        COMBO["time"] = time.time() - start_time
        COMBO["total"] = total_torrents_overall
        if total_torrents_overall == 0:
            span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Result not found"))
            request_counter.add(1, {"status": "empty"})
            return error_handler(
                status_code=status.HTTP_404_NOT_FOUND,
                json_message={"error": "Result not found."},
            )
        request_counter.add(1, {"status": "success"})
        return COMBO


@router.get("/trending")
async def get_all_trending(limit: Optional[int] = 0):
    with tracer.start_as_current_span("get_all_trending") as span:
        span.set_attribute("limit", limit)

        request_counter.add(1, {"status": "requested"})

        start_time = time.time()
        all_sites = check_if_site_available("1337x")
        sites_list = [
            site
            for site in all_sites.keys()
            if all_sites[site]["trending_available"] and all_sites[site]["website"]
        ]
        tasks = []
        COMBO = {"data": []}
        total_torrents_overall = 0
        for site in sites_list:
            limit = (
                all_sites[site]["limit"]
                if limit == 0 or limit > all_sites[site]["limit"]
                else limit
            )
            tasks.append(
                asyncio.create_task(
                    all_sites[site]["website"]().trending(
                        category=None, page=1, limit=limit
                    )
                )
            )
        results = await asyncio.gather(*tasks)
        for res in results:
            if res is not None and len(res["data"]) > 0:
                for torrent in res["data"]:
                    COMBO["data"].append(torrent)
                total_torrents_overall = total_torrents_overall + res["total"]
            else:
                empty_result_counter.add(1, {"site": site})
        COMBO["time"] = time.time() - start_time
        COMBO["total"] = total_torrents_overall
        if total_torrents_overall == 0:
            span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Result not found"))
            request_counter.add(1, {"status": "empty"})
            return error_handler(
                status_code=status.HTTP_404_NOT_FOUND,
                json_message={"error": "Result not found."},
            )
        request_counter.add(1, {"status": "success"})
        return COMBO


@router.get("/recent")
async def get_all_recent(limit: Optional[int] = 0):
    with tracer.start_as_current_span("get_all_recent") as span:
        span.set_attribute("limit", limit)

        request_counter.add(1, {"status": "requested"})

        start_time = time.time()
        all_sites = check_if_site_available("1337x")
        sites_list = [
            site
            for site in all_sites.keys()
            if all_sites[site]["recent_available"] and all_sites[site]["website"]
        ]
        tasks = []
        COMBO = {"data": []}
        total_torrents_overall = 0
        for site in sites_list:
            limit = (
                all_sites[site]["limit"]
                if limit == 0 or limit > all_sites[site]["limit"]
                else limit
            )
            tasks.append(
                asyncio.create_task(
                    all_sites[site]["website"]().recent(category=None, page=1, limit=limit)
                )
            )
        results = await asyncio.gather(*tasks)
        for res in results:
            if res is not None and len(res["data"]) > 0:
                for torrent in res["data"]:
                    COMBO["data"].append(torrent)
                total_torrents_overall = total_torrents_overall + res["total"]
            else:
                empty_result_counter.add(1, {"site": site})
        COMBO["time"] = time.time() - start_time
        COMBO["total"] = total_torrents_overall
        if total_torrents_overall == 0:
            span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, "Result not found"))
            request_counter.add(1, {"status": "empty"})
            return error_handler(
                status_code=status.HTTP_404_NOT_FOUND,
                json_message={"error": "Result not found."},
            )
        request_counter.add(1, {"status": "success"})
        return COMBO