import paho.mqtt.client as mqtt
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorCollection

from cores.config import env
from cores.dependencies import get_logs_collection
from utils.datetime import get_current_datetime

from enums.log import LogStatus
from repositories.log import LogRepository
from services.log import LogService
from utils.logger import logger
from externals.mqtts.publish import publish_log_data


"""NOTE:
Backend only subscribes to MQTT OTA Log Update topic.
So, from the MQTT publisher (ESP32) -> send log update -> backend subs -> save to MongoDB local.

Otherwise, for Monitoring data sensor it will be handled by the frontend (React) directly,
and also for push action start ota update.
"""
def subscribe_message(
    client: mqtt.Client | None,
    main_loop: asyncio.AbstractEventLoop = None
) -> None:
    """
    Subscribe to MQTT messages and process OTA log updates.
    
    Process flow:
    1. Receive message from MQTT broker
    2. Parse the log JSON payload
    3. Create/update document in logs collection with LogModel format
    """
    if main_loop is None:
        raise RuntimeError("Main event loop must be provided from the main thread/event loop.")

    def on_message(client, userdata, msg):
        # Skip processing for retained messages on startup
        is_retained = msg.retain
        if is_retained:
            logger.mqtt_info(f"Skipping retained message on topic {msg.topic}")
            return

        try:
            payload = msg.payload.decode()
            log_data = json.loads(payload)
            logger.mqtt_debug(f"Message received: {log_data}")

            # Extract required information
            required_fields = [
                "session_id", "node_mac", "node_location", 
                "node_type", "node_id", "node_codename", "firmware_version"
            ]
            
            # Validate required fields
            extracted_data = {}
            for field in required_fields:
                value = log_data.get(field)
                if not value:
                    logger.mqtt_error(f"Missing required field: {field}")
                    return
                extracted_data[field] = value

            # Build update fields based on message
            update_fields = {}
            now = get_current_datetime()

            # Normalize message for consistent matching
            message = log_data.get("message", "").strip().lower()

            # Message mapping with proper case handling
            message_handlers = {
                "ota update started": {
                    "download_started_at": now,
                    "flash_status": str(LogStatus.IN_PROGRESS)
                },
                "firmware size ok": {
                    "firmware_size_kb": log_data.get("data", {}).get("size_kb")
                },
                "firmware bytes written": {
                    "bytes_written": log_data.get("data", {}).get("bytes")
                },
                "download time (s)": {
                    "download_duration_sec": log_data.get("data", {}).get("seconds")
                },
                "download speed (kb/s)": {
                    "download_speed_kbps": log_data.get("data", {}).get("speed_kbps")
                },
                "download complete": {
                    "download_completed_at": now
                },
                "ota update complete": {
                    "flash_completed_at": now,
                    "flash_status": str(LogStatus.SUCCESS)
                }
            }

            # Apply message-specific updates
            if message in message_handlers:
                update_fields.update(message_handlers[message])
                logger.mqtt_info(f"Processing message: '{message}' -> {list(update_fields.keys())}")
            else:
                logger.mqtt_warning(f"Unknown message type: '{message}' - skipping update")
                return

            # Process the log asynchronously
            async def upsert_log():
                try:
                    # Get database dependencies
                    logs_collection: AsyncIOMotorCollection = await get_logs_collection()
                    
                    # Create repository and service instances properly
                    log_repository = LogRepository(
                        db=None,  # Will be handled by the dependency
                        logs_collection=logs_collection
                    )
                    log_service = LogService(logs_repository=log_repository)

                    # Process the log with extracted data
                    result_log = await log_service.upsert_log_from_mqtt(
                        session_id=extracted_data["session_id"],
                        node_mac=extracted_data["node_mac"],
                        node_location=extracted_data["node_location"],
                        node_type=extracted_data["node_type"],
                        node_id=extracted_data["node_id"],
                        node_codename=extracted_data["node_codename"],
                        firmware_version=extracted_data["firmware_version"],
                        update_fields=update_fields,
                        log_data=log_data
                    )
                    
                    # If the log was processed successfully, publish the data to the frontend
                    if result_log:
                        logger.db_info(f"Log processed successfully - Codename: '{result_log.node_codename}'")
                        
                        # Convert model to dict for publishing
                        log_dict = result_log.model_dump()
                        
                        # Publish the updated log data to frontend
                        is_pub_success: bool = publish_log_data(client, log_data=log_dict)
                        # Check if the publish was successful
                        if not is_pub_success:
                            logger.mqtt_error("Failed to publish log data to frontend.")
                        else:
                            logger.mqtt_info("Log data published to frontend successfully.")
                    else:
                        logger.db_error("Failed to process log data.")
                except Exception as e:
                    logger.db_error(f"Error during MongoDB upsert: {str(e)}")

            # Run the upsert operation in the main event loop
            future = asyncio.run_coroutine_threadsafe(upsert_log(), main_loop)

            def _log_result(fut):
                try:
                    fut.result()
                except Exception as exc:
                    logger.mqtt_error(f"MongoDB upsert failed: {str(exc)}")

            future.add_done_callback(_log_result)
            
        except KeyError as e:
            logger.mqtt_error(f"Missing key in log data: {str(e)}")
        except json.JSONDecodeError as e:
            logger.mqtt_error(f"JSON decode error: {str(e)}")
        except Exception as e:
            logger.mqtt_error(f"Error processing message: {str(e)}")

    # Check if the MQTT client is initialized
    if client is None:
        logger.mqtt_error("MQTT client is not initialized.")
        return

    # Subscribe to the log topic
    if not client.is_connected():
        logger.mqtt_error("MQTT client is not connected to the broker.")
        return

    logger.mqtt_info(f"Subscribing to topic: {env.MQTT_SUBSCRIBE_TOPIC_LOG} with QoS {env.MQTT_DEFAULT_QOS}")
    client.subscribe(env.MQTT_SUBSCRIBE_TOPIC_LOG, qos=env.MQTT_DEFAULT_QOS)
    client.on_message = on_message