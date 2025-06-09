from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from contextlib import asynccontextmanager
import asyncio

from cores.config import env
from cores.database import start_mongodb_connection, stop_mongodb_connection
from cores.exceptions import validation_exception_handler, http_exception_handler
from utils.logger import logger

from routers.v1.index import router_index
from routers.v1.health import router_health
from routers.v1.node import router_node
from routers.v1.monitoring import router_monitoring
from routers.v1.log import router_log

from middlewares.cors import CORSMiddleware

from externals.firebase.client import init_firebase_app
from externals.mqtts.run import start_mqtt_service, stop_mqtt_service
from externals.gdrive.client import check_gdrive_credentials
from externals.gdrive.client import SERVICE_ACCOUNT_FILE

##### Define lifespan event handler #####
@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    This is used to perform startup and shutdown tasks.
    """
    logger.system_info("LokaSync OTA Backend: Lifespan startup...")

    # ---- Startup tasks ----
    # Task 1: Check MongoDB connection
    logger.system_info("[TASK 1]: Checking MongoDB connection...")
    db_connected = False
    try:
        db_connected = await start_mongodb_connection()
        if db_connected:
            logger.db_info("MongoDB connection is alive")
            db_connected = True
        else:
            logger.db_error("MongoDB connection failed")
    except Exception as e:
        logger.db_error("Error checking MongoDB connection", e)
    
    # Task 2: Start MQTT service
    logger.system_info("[TASK 2]: Starting MQTT service...")
    loop = asyncio.get_running_loop()
    mqtt_client_connected = await loop.run_in_executor(None, start_mqtt_service, loop)

    if mqtt_client_connected:
        logger.mqtt_info("MQTT service started and client is connected (running in background)")
    else:
        logger.mqtt_error("Failed to start MQTT service")
    
    # Task 3: Initialize Firebase Admin SDK
    logger.system_info("[TASK 3]: Initializing Firebase...")
    init_firebase_app()

    # Task 4: Checking Google Drive credential file
    logger.system_info("[TASK 4]: Checking Google Drive credentials...")
    is_gdrive_creds_valid = check_gdrive_credentials(SERVICE_ACCOUNT_FILE)
    if is_gdrive_creds_valid:
        logger.gdrive_info("Google Drive credentials file is valid")
    else:
        logger.gdrive_error("Google Drive credentials file is invalid or not found")
    
    logger.system_info("LokaSync OTA Backend: Lifespan startup sequence finished")

    yield # application runs here

    # ---- Shutdown tasks ----
    logger.system_info("LokaSync OTA Backend: Lifespan shutdown...")
    # Task 1: Stop MongoDB connection
    try:
        if db_connected:
            await stop_mongodb_connection()
            logger.db_info("[TASK 1]: MongoDB connection closed successfully")
    except Exception as e:
        logger.db_error("[TASK 1]: Error closing MongoDB connection", e)
    
    # Task 2: Stop MQTT service
    if mqtt_client_connected:
        await loop.run_in_executor(None, stop_mqtt_service)
        logger.mqtt_info("[TASK 2]: MQTT service stopped successfully")
    else:
        logger.mqtt_warning("[TASK 2]: MQTT service was not running or already stopped")
    
    logger.system_info("LokaSync OTA Backend: Lifespan shutdown completed")


##### Initialize FastAPI application #####
BASE_API_URL: str = f"/api/v{env.API_VERSION}"
app: FastAPI = FastAPI(
    title=env.API_NAME,
    description=env.API_DESCRIPTION,
    version=env.API_VERSION,
    docs_url=f"{BASE_API_URL}/docs",
    redoc_url=f"{BASE_API_URL}/redoc",
    openapi_url=f"{BASE_API_URL}/openapi.json",
    lifespan=_lifespan
)

##### Add middlewares #####
app.add_middleware(
    CORSMiddleware,
    allowed_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173"
        # Add your frontend URLs here
    ],
    allow_credentials=False, # Set to True if you need cookies for auth
    allowed_methods=[
        "OPTIONS", "GET", "POST", "PUT", "DELETE", "PATCH"
    ],
    allowed_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Connection",
        "Host",
        "Origin",
        "Referer",
        "User-Agent",
    ],
    expose_headers=[
        "Content-Disposition",
        "Content-Type",
        "Content-Length",
        "Accept-Ranges"
    ]
)

# Register custom exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

##### Add routes #####
app.include_router(router_index)
app.include_router(router_health, tags=["Health Check"])
app.include_router(router_node, prefix=f"{BASE_API_URL}/node", tags=["Node Management"])
app.include_router(router_monitoring, prefix=f"{BASE_API_URL}/monitoring", tags=["Monitoring Nodes"])
app.include_router(router_log, prefix=f"{BASE_API_URL}/log", tags=["OTA Update Logs"])

logger.system_info(f"FastAPI application initialized - Swagger Docs: {BASE_API_URL}/docs")