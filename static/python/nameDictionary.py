# Lists
def translate_to_display_list(services_list):
    display_names = {
        # DB Name to display name
        "cherryCount": "Conteo de Cerezas",
        "cherryChillHours": "Horas Frío",
        "cherryBudsCount": "Conteo de Dardos",
        "cherryHeatHours": "Horas Calor",
        "cherryChillPortions": "Porciones Frío",
        # Display name to DB Name
        "Conteo de Cerezas": "cherryCount",
        "Horas Frío": "cherryChillHours",
        "Conteo de Dardos": "cherryBudsCount",
        "Horas Calor": "cherryHeatHours",
        "Porciones Frío": "cherryChillPortions",
    }
    return [display_names[item] for item in services_list]

# Single elements

def translate_to_display_element(service):
    display_names = {
        # DB Name to display name
        "cherryCount": "Conteo de Cerezas",
        "cherryChillHours": "Horas Frío",
        "cherryBudsCount": "Conteo de Dardos",
        "cherryHeatHours": "Horas Calor",
        "cherryChillPortions": "Porciones Frío",
        # Display name to DB Name
        "Conteo de Cerezas": "cherryCount",
        "Horas Frío": "cherryChillHours",
        "Conteo de Dardos": "cherryBudsCount",
        "Horas Calor": "cherryHeatHours",
        "Porciones Frío": "cherryChillPortions",
    }
    return display_names[service]

def translate_field_name(field):
    # Ignores the part before the first "-"
    ids = field.split("-")
    field_name = f"{ids[1].capitalize()} {ids[2].capitalize()}"
    return field_name

def services_list():
    return [
        ["cherryCount", "Conteo de Cerezas"], # 0
        ["cherryChillHours", "Reportes Agroclimáticos"], # 1
        ["cherryBudsCount", "Conteo de Dardos"], # 2
        #["cherryHeatHours", "Horas Calor"], # 3
        #["cherryChillPortions", "Porciones Frío"], # 4
    # Add the display name of the services
    ]

def db_code_to_names(dbcode):
    dbcodes = {'FIC_CEREZAS':"Sensores (FIC_CEREZAS)", 
               'FIC_CEREZAS_CONTEO_CEREZAS':"Conteo de Cerezas",
                'FIC_CEREZAS_CONTEO_DARDOS':"Conteo de Dardos",
                 'FIC_CEREZAS_HORAS_FRIO':"Reportes Agroclimáticos"}
    try:
        return dbcodes[dbcode]
    except:
        return "DB code do not exist."