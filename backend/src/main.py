from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from cores.config import env
from cores.database import start_mongodb_connection, stop_mongodb_connection
from routers.v1.index import router_index
from routers.v1.health_check import router_health_check
from routers.v1.firmware import router_firmware
# from routers.v1.log import router_log
from middlewares.request_timeout import RequestTimeoutMiddleware
from middlewares.rate_limiter import init_rate_limiter
from externals.firebase.client import init_firebase_app
from externals.gdrive.client import check_google_drive_credentials
from externals.mqtts.run import start_mqtt_service, stop_mqtt_service

##### Define lifespan event handler #####
@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    This is used to perform startup and shutdown tasks.
    """
    print("🚀 LokaSync OTA Backend: Lifespan startup...")

    # ---- Startup tasks ----
    # Task 1: Check MongoDB connection
    print("\n🔗 [TASK 1]: Checking MongoDB connection...")
    db_connected = False
    try:
        db_connected = await start_mongodb_connection()
        if db_connected:
            print("✅ MongoDB connection is alive.")
            db_connected = True
        else:
            print("❌ MongoDB connection failed.")
    except Exception as e:
        print(f"❌ Error checking MongoDB connection: {str(e)}.")
    
    # Task 2: Start MQTT service
    print("\n🔗 [TASK 2]: Starting MQTT service...")
    loop = asyncio.get_event_loop()
    mqtt_client_connected = await loop.run_in_executor(None, start_mqtt_service)

    if mqtt_client_connected:
        print("✅ MQTT service started and client is connected (running in background).")
    else:
        print("❌ Failed to start MQTT service.")
    
    # Task 3: Initialize Firebase Admin SDK
    print("\n🔐 [TASK 3]: Initializing Firebase...")
    init_firebase_app()
    
    # Task 4: Check Google Drive credentials
    print("\n🧾 [TASK 4]: Checking Google Drive credentials...")
    check_google_drive_credentials()

    print("\n✅ LokaSync OTA Backend: Lifespan startup sequence finished.")

    yield # application runs here

    # ---- Shutdown tasks ----
    print("🔄 LokaSync OTA Backend: Lifespan shutdown...")
    # Task 1: Stop MongoDB connection
    try:
        if db_connected:
            await stop_mongodb_connection()
            print("\n✅ [TASK 1]: MongoDB connection closed successfully.")
    except Exception as e:
        print(f"\n❌ [TASK 1]: Error closing MongoDB connection: {str(e)}.")
    
    # Task 2: Stop MQTT service
    if mqtt_client_connected:
        await loop.run_in_executor(None, stop_mqtt_service)
        print("\n✅ [TASK 2]: MQTT service stopped successfully.")
    else:
        print("\n⚠️  [TASK 2]: MQTT service was not running or already stopped.")
    
    print("\n✅ LokaSync OTA Backend: Lifespan shutdown completed.")


##### Initialize FastAPI application #####
API_VERSION: str = f"/api/v{env.APP_VERSION}"
app: FastAPI = FastAPI(
    title=env.APP_NAME,
    description=env.APP_DESCRIPTION,
    version=env.APP_VERSION,
    docs_url=f"{API_VERSION}/docs",
    redoc_url=f"{API_VERSION}/redoc",
    openapi_url=f"{API_VERSION}/openapi.json",
    lifespan=_lifespan
)

##### Add middlewares #####
app.add_middleware(
    CORSMiddleware,
    allow_origins=env.MIDDLEWARE_CORS_ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTimeoutMiddleware, timeout_seconds=env.MIDDLEWARE_REQUEST_TIMEOUT_SECOND)
init_rate_limiter(app)

##### Add routes #####
app.include_router(router_index)
app.include_router(router_health_check, tags=["Health Check"])
app.include_router(router_firmware, prefix=f"{API_VERSION}", tags=["Firmware"])
# app.include_router(router_monitoring, prefix=f"{API_VERSION}", tags=["Monitoring"])
# app.include_router(router_log, prefix=f"{API_VERSION}", tags=["Log"])