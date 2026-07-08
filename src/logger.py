import logging
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Configure Logging
log_file_path = os.path.join("data", "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()  # This will also print logs to terminal
    ]
)

logger = logging.getLogger("InvoiceSystem")