import os
import logging

logger = logging.getLogger("brand-guardian-telemetry")


def setup_telemetry():
    """
    Optionally enables Azure Monitor OpenTelemetry.
    If APPLICATIONINSIGHTS_CONNECTION_STRING is not set, this is a no-op.
    If the azure-monitor package is not installed, logs a warning and continues.
    This will never crash the app — telemetry is purely optional.
    """
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.info("Telemetry disabled (APPLICATIONINSIGHTS_CONNECTION_STRING not set).")
        return

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(
            connection_string=connection_string,
            logger_name="brand-guardian-tracer"
        )
        logger.info("Azure Monitor telemetry enabled.")
    except ImportError:
        logger.warning(
            "azure-monitor-opentelemetry not installed. "
            "Telemetry disabled. Install it to enable Azure Monitor."
        )
    except Exception as e:
        logger.error(f"Failed to initialize Azure Monitor: {e}")
        # Never raise — telemetry failure must not crash the API server