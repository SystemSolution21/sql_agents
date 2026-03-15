# Import built-in libraries
from pathlib import Path

import requests

# Import dotenv libraries
from dotenv import load_dotenv

# Import langchain libraries
from langchain_community.utilities import SQLDatabase

# Import local libraries
from utils.logger import SqlAgentLog

# Initialize logger
logger = SqlAgentLog.get_logger(module_name=__name__)

# Load environment variables
load_dotenv()

# Get database
url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"

# Set database path
DB_PATH: Path = Path("Chinook.db")

if DB_PATH.exists():
    logger.info(msg=f"{DB_PATH} already exists, skipping download.")
else:
    response: requests.Response = requests.get(url)
    if response.status_code == 200:
        DB_PATH.write_bytes(data=response.content)
        logger.info(msg=f"{DB_PATH} downloaded successfully.")
    else:
        logger.error(
            msg=f"Failed to download the file. Status code: {response.status_code}"
        )

# Load database
db: SQLDatabase = SQLDatabase.from_uri(database_uri="sqlite:///Chinook.db")
if db:
    logger.info(msg="Database loaded successfully.")
else:
    logger.error(msg="Failed to load database.")

print(f"Dialect: {db.dialect}")
print(f"Available tables: {db.get_usable_table_names()}")
print(f"Sample output: {db.run('SELECT * FROM Artist LIMIT 5;')}")
