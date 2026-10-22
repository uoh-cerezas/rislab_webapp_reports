import pymongo
import os
from urllib.parse import quote_plus
from datetime import datetime, timezone

from static.python.nameDictionary import (
    translate_to_display_list,
    translate_field_name,
    translate_to_display_element,
)


def hash_password(by, pw):
    # Returns a hashed string
    pw_hash = by.generate_password_hash(pw)
    return pw_hash.decode("utf-8")


def check_password(stored_hash, password, by):
    return by.check_password_hash(stored_hash, password)


# Login connection to database
def database_login(by, mail, password):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["users"]
        results = collection.find({"loginData.mail": mail})
        exit_code = None
        doc_count = False
        # Session data
        session_data = {}
        # Iterate over docs
        for r in results:
            doc_count = True
            if check_password(r["loginData"]["password"], password, by):
                # If passwords match
                session_data = {
                    "role": r["loginData"]["role"],
                    "name": r["loginData"]["name"],
                    "verified": r["loginData"]["verified"],
                    "cherryCount": r["services"]["cherryCount"]["active"],
                    "cherryChillHours": r["services"]["cherryChillHours"]["active"],
                    "cherryBudsCount": r["services"]["cherryBudsCount"]["active"],
                    "fieldsCherryCount": r["services"]["cherryCount"]["fields"],
                    "fieldsChillHours": r["services"]["cherryChillHours"]["fields"],
                    "fieldsBudsCount": r["services"]["cherryBudsCount"]["fields"],
                }
                # Exit code 0 for successful login
                exit_code = 0
            else:
                # If passwords dont match
                # Exit code 2 for wrong password
                exit_code = 2
        if not doc_count:
            # If no doc found means the consulted mail is not in the database
            # Exit code 1 for not registered mails
            exit_code = 1
        client.close()
        return exit_code, session_data

    except Exception as e:
        print("sdfaasfdsdf",e)
        exit_code = 3


def database_get_cherry_count_reports(fields):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    exit_code = None
    try:
        database = client["FIC_CEREZAS_CONTEO_CEREZAS"]
        field_data = []
        for field in fields.keys():
            collection = database[field]
            results = collection.find({})
            doc_count = False
            # Iterate over docs
            for r in results:
                dict_r = dict(r)
                dict_r["field"] = field
                doc_count = True
                field_data.append(dict_r)
            if not doc_count:
                # If no doc found means the consulted mail is not in the database
                # Exit code 1 for not registered mails
                exit_code = 1
        client.close()
        field_data = sorted(field_data, key=lambda x: int(x["date"]), reverse=True)
        return exit_code, field_data

    except Exception as e:
        print(e)
        exit_code = 3


def database_get_chill_hours_reports(fields):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    exit_code = None
    try:
        database = client["FIC_CEREZAS_HORAS_FRIO"]
        field_data = []
        for field in fields.keys():
            collection = database[field]
            results = collection.find({})
            doc_count = False
            # Iterate over docs
            for r in results:
                dict_r = dict(r)
                doc_count = True
                field_data.append(dict_r)
            if not doc_count:
                # If no doc found means the consulted mail is not in the database
                # Exit code 1 for not registered mails
                exit_code = 1
        client.close()
        field_data = sorted(field_data, key=lambda x: int(x["out-date"]), reverse=True)

        return exit_code, field_data

    except Exception as e:
        print(e)
        exit_code = 3

def database_get_heat_hours_reports(fields):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    exit_code = None
    try:
        database = client["FIC_CEREZAS_ACUMULACION_CALOR"]
        field_data = []
        for field in fields.keys():
            collection = database[field]
            results = collection.find({})
            doc_count = False
            # Iterate over docs
            for r in results:
                dict_r = dict(r)
                doc_count = True
                field_data.append(dict_r)
            if not doc_count:
                # If no doc found means the consulted mail is not in the database
                # Exit code 1 for not registered mails
                exit_code = 1
        client.close()
        field_data = sorted(field_data, key=lambda x: int(x["out-date"]), reverse=True)

        return exit_code, field_data

    except Exception as e:
        print(e)
        exit_code = 3

def database_get_chill_portions_reports(fields):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    exit_code = None
    try:
        database = client["FIC_CEREZAS_PORCIONES_FRIO"]
        field_data = []
        for field in fields.keys():
            collection = database[field]
            results = collection.find({})
            doc_count = False
            # Iterate over docs
            for r in results:
                dict_r = dict(r)
                doc_count = True
                field_data.append(dict_r)
            if not doc_count:
                # If no doc found means the consulted mail is not in the database
                # Exit code 1 for not registered mails
                exit_code = 1
        client.close()
        field_data = sorted(field_data, key=lambda x: int(x["out-date"]), reverse=True)

        return exit_code, field_data

    except Exception as e:
        print(e)
        exit_code = 3


def database_get_field_coordinates(field_name):
    """
    Recupera las coordenadas (lat, lng) de un campo desde FIC_CEREZAS.
    Busca en la colección del campo, el atributo sensor_static_data
    y extrae sensor_lat y sensor_lon del primer sensor que encuentre.
    Retorna: {"lat": float, "lng": float} o None si no encuentra
    """
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        # FIC_CEREZAS -> nombre_campo -> sensor_static_data -> sensor_lat y sensor_lon
        database = client["FIC_CEREZAS"]
        collection = database[field_name]
        # Buscar el primer documento que tenga sensor_static_data
        result = collection.find_one({"sensor_static_data": {"$exists": True}})
        if result and "sensor_static_data" in result:
            sensor_data = result["sensor_static_data"]
            sensor_lat = sensor_data.get("sensor_lat")
            sensor_lon = sensor_data.get("sensor_lon")
            if sensor_lat is not None and sensor_lon is not None:
                client.close()
                return {"lat": float(sensor_lat), "lng": float(sensor_lon)}
        client.close()
        return None
    except Exception as e:
        print(e)
        return None


def database_get_buds_count_reports(fields):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    exit_code = None
    try:
        database = client["FIC_CEREZAS_CONTEO_DARDOS"]
        field_data = []
        for field in fields.keys():
            collection = database[field]
            results = collection.find({})
            doc_count = False
            # Iterate over docs
            for r in results:
                dict_r = dict(r)
                dict_r["field"] = field
                doc_count = True
                field_data.append(dict_r)
            if not doc_count:
                # If no doc found means the consulted mail is not in the database
                # Exit code 1 for not registered mails
                exit_code = 1
        client.close()
        field_data = sorted(field_data, key=lambda x: int(x["date"]), reverse=True)
        return exit_code, field_data

    except Exception as e:
        print(e)
        exit_code = 3


def database_get_cherry_count_report_info(field, zone, date, name):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_CONTEO_CEREZAS"]
        collection = database[field]
        results = collection.find_one({"zone": int(zone), "date": date, "name": name})
        exit_code = 1
        if results != None:
            exit_code = 0
        client.close()
        return exit_code, dict(results)

    except Exception as e:
        print(e)
        exit_code = 3


def database_get_buds_count_report_info(field, zone, date, name):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_CONTEO_DARDOS"]
        collection = database[field]
        results = collection.find_one({"zone": int(zone), "date": date, "name": name})
        exit_code = 1
        if results != None:
            exit_code = 0
        client.close()
        return exit_code, dict(results)
        
    except Exception as e:
        print(e)
        exit_code = 3

def database_reVerifiedToken(mail):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["users"]
        noverified_user = collection.find_one({"loginData.mail": mail})
        exit_code = 1
        if noverified_user == {}:
            exit_code = 2
            return exit_code, None
        
        token = noverified_user["loginData"]["verification_token"]
        client.close()
        
        return exit_code, token

    except Exception as e:
        print(e)
        exit_code = 3
        return exit_code, None



def database_isVerified(tk):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["users"]
        is_verified = collection.update_one({"loginData.verification_token": tk},{"$set": {"loginData.verified": True}} )
        exit_code = 1
        if is_verified.matched_count == 0:
            exit_code = 2
        client.close()
        return exit_code

    except Exception as e:
        print(e)
        exit_code = 3

def database_add_user(by, name, mail, password, services, role,token):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["users"]
        emails_list = database_get_users_list()[1]
        already_existing = mail in emails_list
        if already_existing:
            return 0, already_existing

        user_doc = {
            "loginData": {
                "name": name,
                "mail": mail,
                "password": hash_password(by, password),
                "verification_token":token,
                "verified":False,
                "role": int(role),
            },
            "services": {
                "cherryChillHours": {"active": services[0], "fields": {}},
                "cherryCount": {"active": services[0], "fields": {}},   
                "cherryBudsCount": {"active": services[0], "fields": {}},
                #  "nameOfTheNewService": {"active": services[number],"fields": {}}, <- STRUCTURE WHEN NEW SERVICES ARE ADDED
            },
        }
        collection.insert_one(user_doc)
        client.close()
        return 0, already_existing

    except Exception as e:
        exit_code = 1
        print(e)
        return exit_code,e

def database_mod_user(mail, services, role):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["users"]
        collection.update_one(
            {"loginData.mail": mail},
            {
                "$set": {
                    "loginData.role": int(role),
                    "services.cherryCount.active": services[0],
                    "services.cherryChillHours.active": services[1],
                    "services.cherryBudsCount.active": services[2]
                    # "services.nameOfTheNewService.active": service[number], <- STRUCTURE WHEN NEW SERVICES ARE ADDED
                }
            },
        )
        # "cherryCount": "Conteo de Cerezas",
        # "cherryChillHours": "Horas Frío",
        # "cherryBudsCount"
        # "cherryHeatHours"
        # "cherryChillPortions"
        client.close()
        return 0

    except Exception as e:
        print(e)
        exit_code = 1


def database_get_users_list():
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["users"]
        available_usernames = [
            doc["loginData"]["mail"]
            for doc in collection.find({}, {"_id": 0, "loginData.mail": 1})
        ]

        # results = collection.find({"zone":zone})
        exit_code = None
        doc_count = False
        client.close()

        return exit_code, available_usernames

    except Exception as e:
        print(e)
        exit_code = 3


def database_get_services_list():
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        dbs = client.list_database_names()
        # dbs.remove("admin","config","local","FIC_CEREZAS_WEB")

        services_db = [
            db
            for db in dbs
            if db not in ["admin", "config", "local", "FIC_CEREZAS_WEB","FIC_CEREZAS_PORCIONES_FRIO","FIC_CEREZAS_ACUMULACION_CALOR"]
        ]
        exit_code = None
        doc_count = False
        client.close()
        return services_db

    except Exception as e:
        print(e)
        exit_code = 3


def delete_user(mail):
    # conexion a bd
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["users"]
        delete_result = collection.delete_many({"loginData.mail": mail})
        deleted_count = (
            delete_result.deleted_count
            if hasattr(delete_result, "deleted_count")
            else 0
        )
        print(f"Usuarios eliminados: {deleted_count}")
        client.close()
        return deleted_count
    except Exception as e:
        print(f"Error en delete_user: {e}")
        client.close()
        return 0


def database_add_service(db_name, field_name):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        existing_dbs = client.list_database_names()
        already_existing = db_name in existing_dbs
        # Name is already being used in the client
        if already_existing:
            return 0, already_existing
        # Name isnt being used
        new_db = client[db_name]
        new_col = new_db[field_name]
        new_col.insert_one({"_id": None})

        # Add it to the notifications db

        # user_collection.update_one({"loginData.mail": mail},
        #                         {"$push": {f"services.{service}.fields.{field}": int(quarter) } })

        db = client["FIC_CEREZAS_WEB"]
        noti_collection = db["notifications"]
        noti_doc = {"service": db_name, "fields": {field_name: False}}
        noti_collection.insert_one(noti_doc)

        client.close()
        return 0, already_existing

    except Exception as e:
        print(e)
        exit_code = 1


def database_add_field(service, field_name):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client[service]
        collections = database.list_collection_names()
        already_exist = field_name in collections
        # Name is already being used in the client
        if already_exist:
            return 0, already_exist
        # Name isnt being used
        new_col = database[field_name]
        new_col.insert_one({"_id": None})

        # Add it to the notifications db

        db = client["FIC_CEREZAS_WEB"]
        noti_collection = db["notifications"]
        noti_collection.update_one(
            {"service": service}, {"$set": {f"fields.{field_name}": False}}
        )

        client.close()
        return 0, already_exist

    except Exception as e:
        print(e)
        exit_code = 1


def check_duplicated_field(service, field_name):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client[service]
        collections = database.list_collection_names()
        already_exist = field_name in collections
        # Name is already being used in the client
        client.close()
        return already_exist

    except Exception as e:
        print(e)
        exit_code = 1


def check_user_fields_and_zones(mail, service, field, zone):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        user_collection = user_database["users"]
        user_info = user_collection.find_one({"loginData.mail": mail})

        # check service and active == true
        services = user_info.get("services", {})

        if service not in services or services[service].get("active") == False:
            client.close()
            print("no service or inactive")
            return False, False

        user_fields = services[service].get("fields", {})

        if field not in user_fields:
            client.close()
            return True, False
        else:
            # revisar zonas 'nombre-campo' [zona1, zona2, zona3]
            user_zones = user_fields[field]
            for field_zones in user_zones:
                if int(zone) == field_zones:
                    client.close()
                    return True, True
            client.close()
            return True, False

    except Exception as e:
        print(e)
        return False, False


def check_duplicated_quarter(mail, service, field, quarter):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        user_collection = user_database["users"]
        user_info = user_collection.find_one({"loginData.mail": mail})

        already_exist = False
        user_fields = user_info["services"][f"{service}"]["fields"]

        if field in user_fields:
            f_quarters = user_fields[f"{field}"]
            if int(quarter) in f_quarters:
                already_exist = True
                client.close()
                return already_exist
            elif quarter not in f_quarters:
                client.close()
                return already_exist
        elif field not in user_fields:
            client.close()
            return already_exist

    except Exception as e:
        print(e)
        exit_code = 1

    # try:
    #     user_database = client["FIC_CEREZAS_WEB"]
    #     user_collection = user_database["users"]
    #     user_info = user_collection.find_one({"loginData.mail": mail})

    #     f_exists = False
    #     user_fields = user_info["services"][f"{service}"]["fields"]
    #     if field in user_fields:
    #         f_quarters = user_fields[f"{field}"]
    #         if int(quarter) in f_quarters:
    #             f_exists = True
    #         elif quarter not in f_quarters:
    #             # quarters_count = len(field_quarters)
    #             user_collection.update_one({"loginData.mail": mail},
    #                                     {"$push": {f"services.{service}.fields.{field}": int(quarter) } })
    #                                         # {"$push": {"services.service1.attr1.field1": 4}}
    #     elif field not in user_fields:
    #         user_collection.update_one({"loginData.mail": mail},
    #                                     {"$set": {f"services.{service}.fields.{field}": [ int(quarter) ] } })
    #     client.close()


def database_list_user_services(user_mail):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        user_collection = database["users"]
        user_data = user_collection.find_one({"loginData.mail": user_mail})
        available_services = [
            service
            for service, status in user_data["services"].items()
            if status.get("active") is True
        ]
        # available_services = ["A","B","C","D"]
        display_services_list = []
        for service in available_services:
            display_services_list.append(
                [translate_to_display_element(service), service]
            )

        return display_services_list

    except Exception as e:
        print(e)
        exit_code = 1


def fields_by_service(mail, service):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        user_collection = database["users"]
        user_data = user_collection.find_one({"loginData.mail": mail})
        available_fields = [
            field for field, status in user_data["services"][service]["fields"].items()
        ]

        return available_fields

    except Exception as e:
        print(e)
        exit_code = 1


def database_list_service_fields(service):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        if service == "cherryCount":
            database = client["FIC_CEREZAS"]
            fields_list = database.list_collection_names()
            display_fields_list = []
            for field in fields_list:
                ids = field.split("-")
                field_name = f"{ids[1].capitalize()} {ids[2].capitalize()}"
                display_fields_list.append([field_name, field])
            sorted_display = sorted(display_fields_list, key=lambda x: x[0])
            return sorted_display
        elif service == "cherryChillHours":
            database = client["FIC_CEREZAS"]
            fields_list = database.list_collection_names()
            display_fields_list = []
            for field in fields_list:
                ids = field.split("-")
                field_name = f"{ids[1].capitalize()} {ids[2].capitalize()}"
                display_fields_list.append([field_name, field])
            sorted_display = sorted(display_fields_list, key=lambda x: x[0])
            return sorted_display
        elif service == "cherryBudsCount":
            database = client["FIC_CEREZAS"]
            fields_list = database.list_collection_names()
            display_fields_list = []
            for field in fields_list:
                ids = field.split("-")
                field_name = f"{ids[1].capitalize()} {ids[2].capitalize()}"
                display_fields_list.append([field_name, field])
            sorted_display = sorted(display_fields_list, key=lambda x: x[0])
            return sorted_display
        elif service == "cherryHeatHours":
            # MUST CREATE THE CORRECT DATABASE
            return ["NO DATABASE", "NO DATABASE", "NO DATABASE"]
        elif service == "cherryChillPortions":
            database = client["FIC_CEREZAS"]
            fields_list = database.list_collection_names()
            display_fields_list = []
            for field in fields_list:
                ids = field.split("-")
                field_name = f"{ids[1].capitalize()} {ids[2].capitalize()}"
                display_fields_list.append([field_name, field])
            sorted_display = sorted(display_fields_list, key=lambda x: x[0])
            return sorted_display
        elif service == "testS":
            database = client["testS"]
            display_fields_list = []
            for field in fields_list:
                field_name = field
                display_fields_list.append([field_name, field])
            sorted_display = sorted(display_fields_list, key=lambda x: x[0])
            return sorted_display

    except Exception as e:
        print(e)
        exit_code = 1


def database_get_user_role(mail):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        user_collection = user_database["users"]
        user_info = user_collection.find_one({"loginData.mail": mail})
        user_role = user_info["loginData"]["role"]
        return user_role

    except Exception as e:
        print(e)
        exit_code = 1


def database_add_user_field(service, field, mail, quarter):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        user_collection = user_database["users"]
        user_info = user_collection.find_one({"loginData.mail": mail})

        f_exists = False
        user_fields = user_info["services"][f"{service}"]["fields"]
        if field in user_fields:
            f_quarters = user_fields[f"{field}"]
            if int(quarter) in f_quarters:
                f_exists = True
            elif quarter not in f_quarters:
                # quarters_count = len(field_quarters)
                user_collection.update_one(
                    {"loginData.mail": mail},
                    {"$push": {f"services.{service}.fields.{field}": int(quarter)}},
                )
                # {"$push": {"services.service1.attr1.field1": 4}}
        elif field not in user_fields:
            user_collection.update_one(
                {"loginData.mail": mail},
                {"$set": {f"services.{service}.fields.{field}": [int(quarter)]}},
            )
        client.close()
        # return 0, exists
        return 0, f_exists

    except Exception as e:
        print(e)
        exit_code = 1


def turn_notification_on(service, field):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        notification_col = user_database["notifications"]
        notification_col.update_one(
            {"service": service}, {"$set": {f"fields.{field}": True}}
        )

        return 0

    except Exception as e:
        print(e)
        exit_code = 1


def turn_notification_off(service, fields_off_list):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        notification_col = user_database["notifications"]
        # service_doc = notification_col.find_one({"service": service})

        # Query
        update_fields = {f"fields.{field}": False for field in fields_off_list}

        notification_col.update_one({"service": service}, {"$set": update_fields})

        client.close()
        if service == "cherryCount":
            return "/reportes_cherrycount"

        elif service == "cherryChillHours":
            return "/reportes_chillhours"

        elif service == "cherryBudsCount":
            return "/reportes_budscount"

        elif service == "cherryHeatHours":
            return "/reportes_chillhours"

        elif service == "cherryChillPortions":
            return "/reportes_chillportions"

    except Exception as e:
        print(e)
        exit_code = 1


def notifications_off(service, mail):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        notification_col = user_database["notifications"]
        # service_doc = notification_col.find_one({"service": service})

        pending_notifications = list_pending_notifications(mail)

        fields_off_list = []

        for i in pending_notifications:
            if i[0] == service:
                for j in i[1]:
                    fields_off_list.append(j)

        # Query
        update_fields = {f"fields.{field}": False for field in fields_off_list}

        notification_col.update_one({"service": service}, {"$set": update_fields})

        client.close()

    except Exception as e:
        print(e)
        exit_code = 1

    finally:
        client.close()


def list_pending_notifications(mail):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        user_database = client["FIC_CEREZAS_WEB"]
        notifications = user_database["notifications"]
        user_services = database_list_user_services(
            mail
        )  # [ ["Conteo de Cerezas","cherryCount"], ["...","..."], ... ]
        pending_notifications = []

        for s in user_services:
            service_fields_list = [s[1]]  # The list of each service, eg ["cherryCount"]
            fields_list = []  # List of fields active on said service for this user
            active_fields = fields_by_service(mail, s[1])
            noti = notifications.find_one({"service": s[1]})
            if noti and noti["fields"] != {}:
                for field, notification in noti["fields"].items():
                    if notification and field in active_fields:
                        fields_list.append(field)  # ["field-1","field-2","field-3"...]
                        # break
            if fields_list != []:  # if there service has active notifications:
                service_fields_list.append(
                    fields_list
                )  # ["cherryCount", ["field-1","field-2","field-3"...]]
                pending_notifications.append(
                    service_fields_list
                )  # [ ["cherryCount", ["field-1","field-2","field-3"...]], ["cherryBudsCount", ["field-1","field-2","field-3"...]] ]
                # 1 element in the array represents 1 service => array[i]. array[i][0] contains the service name. array[i][1] contains the fields with active notifications on that service for this user.

        # for s in user_services:
        #     active_fields = fields_by_service(mail,s[1])
        #     noti = notifications.find_one({"service": s[1]})
        #     if noti and noti["fields"] != {}:
        #         for field, notification in noti["fields"].items():
        #             if notification and field in active_fields:
        #                 s.append(field)
        #                 s.append(translate_field_name(field))
        #                 pending_notifications.append( s )
        #                 break

        # unique_pending = list({element[1] for element in pending_notifications})
        return pending_notifications

    except Exception as e:
        print(e)
        exit_code = 1


def database_increment_report_id(service, field):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["reports-id"]
        query = {"service": service}
        new_data = {"$inc": {"fields." + field: 1}}
        collection.update_one(query, new_data)
        client.close()
        return 0

    except Exception as e:
        print(e)
        exit_code = 1
        return exit_code
    finally:
        client.close()


def database_get_report_id(service, field):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS_WEB"]
        collection = database["reports-id"]
        result = collection.find_one({"service": service})
        if not result or "fields" not in result:
            return 0, 1
        dict_r = dict(result)
        r_id = dict_r["fields"][field]
        return 0, r_id

    except Exception as e:
        print(e)
        exit_code = 1
        return exit_code, None
    finally:
        client.close()


def database_add_agroclimate_report(service, field_name, zone, in_date, out_date, name):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017

    format_string = "%Y-%m-%d"

    date_object_in = datetime.strptime(in_date, format_string)

    unix_timestamp_in = str(int(date_object_in.timestamp()))

    date_object_out = datetime.strptime(out_date, format_string)

    unix_timestamp_out = str(int(date_object_out.timestamp()))

    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client[service]
        collection = database[field_name]
        collection.insert_one(
            {
                "data-field": field_name,
                "zone": zone,
                "in-date": unix_timestamp_in,
                "out-date": unix_timestamp_out,
                "name": name,
            }
        )
        client.close()
        return 0

    except Exception as e:
        print(e)
        exit_code = 1

def database_get_chill_hours_report_info(field, zone, in_date, out_date):
    db_username = quote_plus(os.environ["USER"])
    db_password = quote_plus(os.environ["PASS"])
    db_host = os.environ["HOST"]
    port = 27017
    fecha_inicio = datetime.fromtimestamp(in_date, tz=timezone.utc)
    fecha_fin = datetime.fromtimestamp(out_date, tz=timezone.utc)
    fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    fecha_fin_str = fecha_fin.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    # Connection
    uri = f"mongodb://{db_username}:{db_password}$@{db_host}:{port}"
    client = pymongo.MongoClient(uri)
    try:
        database = client["FIC_CEREZAS"]
        collection = database[field]
        cursor = collection.find({
            "sensor_static_data.sensor_zone": {
                "$in": [int(zone), str(zone)]                                   
            },
            "time_sensor_tx": {
                "$gte": fecha_inicio_str,
                "$lte": fecha_fin_str
            }
        })
        exit_code = 1
       
        results = list(cursor)
        
        client.close()
        return exit_code, results
        
    except Exception as e:
        print(e)
        exit_code = 3