import subprocess
from datetime import datetime
from urllib.parse import quote_plus
import os

db_username = os.environ["MONGO_USER"]
db_password = os.environ["MONGO_PASSWORD"]
db_host = os.environ["MONGO_HOST"]
port = int(os.environ.get("MONGO_PORT", "27017"))
db_names = [name for name in os.environ.get("MONGO_DATABASES", "").split(",") if name]
if not db_names:
    raise RuntimeError("Set MONGO_DATABASES to a comma-separated database list")

encoded_password = quote_plus(db_password)

for db_name in db_names:
    MONGO_URI = (
        f"mongodb://{db_username}:{encoded_password}"
        f"@{db_host}:{port}/{db_name}"
        f"?authSource=admin"
    )

    BACKUP_DIR = os.path.expanduser("~/mongo_backups")

    date = datetime.now().strftime("%Y-%m-%d")

    cmd = [
        "mongodump",
        f"--uri={MONGO_URI}",
        f"--out={BACKUP_DIR}/mongo_{db_name}_{date}"
    ]

    subprocess.run(cmd, check=True)
print("Backup completed successfully")
