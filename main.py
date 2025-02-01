import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.v1.search_router import router as search_router
from routers.v1.trending_router import router as trending_router
from routers.v1.catergory_router import router as category_router
from routers.v1.recent_router import router as recent_router
from routers.v1.combo_routers import router as combo_router
from routers.v1.sites_list_router import router as site_list_router
from routers.home_router import router as home_router
from routers.v1.search_url_router import router as search_url_router
from helper.uptime import getUptime
from mangum import Mangum
from math import ceil
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server

resource = Resource(attributes={
    "service.name": "Torrent-Api-Py"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer_provider = trace.get_tracer_provider()

otlp_exporter = OTLPSpanExporter(endpoint="tempo-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

start_http_server(port=8000, addr="0.0.0.0")
prometheus_reader = PrometheusMetricReader()
meter_provider = MeterProvider(resource=resource, metric_readers=[prometheus_reader])

def init_telemetry(app):
    FastAPIInstrumentor.instrument_app(app)

startTime = time.time()

app = FastAPI(
    title="Torrent-Api-Py",
    version="1.0.1",
    description=f"Unofficial Torrent-Api",
    docs_url="/docs",
    contact={
        "name": "Neeraj Kumar",
        "url": "https://github.com/ryuk-me",
        "email": "neerajkr1210@gmail.com",
    },
)

init_telemetry(app)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_route(req: Request):
    """
    Health Route : Returns App details.
    """
    return JSONResponse(
        {
            "app": "Torrent-Api-Py",
            "version": "v" + "1.0.1",
            "ip": req.client.host,
            "uptime": ceil(getUptime(startTime)),
        }
    )

app.include_router(search_router, prefix="/api/v1/search")
app.include_router(trending_router, prefix="/api/v1/trending")
app.include_router(category_router, prefix="/api/v1/category")
app.include_router(recent_router, prefix="/api/v1/recent")
app.include_router(combo_router, prefix="/api/v1/all")
app.include_router(site_list_router, prefix="/api/v1/sites")
app.include_router(search_url_router, prefix="/api/v1/search_url")
app.include_router(home_router, prefix="")

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)