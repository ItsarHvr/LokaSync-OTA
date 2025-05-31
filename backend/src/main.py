from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from contextlib import asynccontextmanager
import asyncio

from cores.config import env
from cores.database import start_mongodb_connection, stop_mongodb_connection
from cores.exceptions import validation_exception_handler, http_exception_handler

from routers.v1.index import router_index
from routers.v1.health import router_health
from routers.v1.node import router_node
from routers.v1.monitoring import router_monitoring
from routers.v1.log import router_log

from externals.firebase.client import init_firebase_app
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
    loop = asyncio.get_running_loop()
    mqtt_client_connected = await loop.run_in_executor(None, start_mqtt_service, loop)

    if mqtt_client_connected:
        print("✅ MQTT service started and client is connected (running in background).")
    else:
        print("❌ Failed to start MQTT service.")
    
    # Task 3: Initialize Firebase Admin SDK
    print("\n🔐 [TASK 3]: Initializing Firebase...")
    init_firebase_app()
    
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

# Register custom exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

##### Add routes #####
app.include_router(router_index)
app.include_router(router_health, tags=["Health Check"])
app.include_router(router_node, prefix=f"{API_VERSION}/node", tags=["Node Management"])
app.include_router(router_monitoring, prefix=f"{API_VERSION}/monitoring", tags=["Monitoring Nodes"])
app.include_router(router_log, prefix=f"{API_VERSION}/log", tags=["OTA Update Logs"])