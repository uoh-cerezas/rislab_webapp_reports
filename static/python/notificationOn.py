import pymongo
import os
from urllib.parse import quote_plus
from datetime import datetime

def turn_notification_on(service, field):

    db_username = quote_plus(os.environ['USER'])
    db_password = quote_plus(os.environ['PASS'])
    db_host = os.environ['HOST']
    port = 27017
    #Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        notification_col = user_database["notifications"]
        notification_col.update_one({"service": service},
                                    {"$set": {f"fields.{field}": True } })

        return 0

    except Exception as e:
        print(e)
        exit_code = 1