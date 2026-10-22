import os

# from datetime import datetime

# Variables de sesion:
# session = {"usuario": "fsanchez", "servicio": 1, "campo": "Coinco", "cuartel": "01"}


# def crear_carpeta():
#     usuario = session["usuario"]
#     servicio = session["servicio"]
#     campo = session["campo"]
#     cuartel = session["cuartel"]
#     try:
#         # Ruta del script actual
#         ruta_actual = os.path.dirname(os.path.abspath(__file__))
#         # Ruta completa a la carpeta 'users'
#         ruta_users = os.path.join(ruta_actual, "users")
#         mi_path = ruta_actual + ruta_users

#         # Crear la carpeta principal dentro de 'users'
#         ruta_carpeta = os.path.join(ruta_users, usuario)  # actualizar directorio

#         os.makedirs(ruta_carpeta, exist_ok=True)  # crear carpeta
#         print(f"Carpeta '{ruta_carpeta}' creada o ya existente.")
#         mi_path = mi_path + ruta_carpeta

#         # Crear la subcarpeta del servicio en cuestion
#         if servicio == 1:  # Caso conteo de cerezas
#             ruta_servicio = os.path.join(ruta_carpeta, "cherrycount")
#             os.makedirs(ruta_servicio, exist_ok=True)
#             print(f"Subcarpeta '{ruta_servicio}' creada o ya existente.")
#         elif servicio == 2:  # Caso reporte agroclimatico
#             ruta_servicio = os.path.join(ruta_carpeta, "agroreport")
#             os.makedirs(ruta_servicio, exist_ok=True)
#             print(f"Subcarpeta '{ruta_servicio}' creada o ya existente.")
#         mi_path = mi_path + ruta_servicio

#         # Crear subcarpeta de reporte campo y cuartel
#         ahora = datetime.now()  # tiempo tomado en el momento
#         nombre_carpeta = f"{ahora.date()}{ahora.time()}_{campo}_{cuartel}".replace(
#             ":", "_"
#         )

#         ruta_reporte = os.path.join(ruta_servicio, nombre_carpeta)

#         os.makedirs(ruta_reporte, exist_ok=True)
#         print(f"Subcarpeta '{ruta_reporte}' creada o ya existente.")
#         mi_path = ruta_reporte  # <-- Aqui esta guardada la ruta completa

#     except Exception as e:
#         # Caso error
#         print(f"Ocurrió un error: {e}")


# def crear_carpeta2(usuario, servicios, fields, cuarteles, ruta):
#     try:
#         # usuario/servicio/campo
#         # ruta_actual = os.path.dirname(os.path.abspath(__file__))

#         # Ruta completa a la carpeta 'users'
#         ruta_users = os.path.join(ruta, "users")
#         # Dashboard/users

#         # Crear la carpeta principal dentro de 'users'
#         ruta_carpeta = os.path.join(
#             ruta_users, usuario
#         )  # actualizar directorio: # Dashboard/users/areyes/

#         os.makedirs(ruta_carpeta, exist_ok=True)  # crear carpeta /areyes

#         # Crear la subcarpeta del servicio en cuestion
#         if servicios == 1:  # Caso solo conteo de cerezas
#             ruta_servicio1 = os.path.join(
#                 ruta_carpeta, "cherryCount"
#             )  # actualizar directorio: Dashboard/users/areyes/cherryCount
#             os.makedirs(ruta_servicio1, exist_ok=True)  # crear carpeta
#         elif servicios == 2:  # Caso solo reporte agroclimatico
#             ruta_servicio2 = os.path.join(ruta_carpeta, "agroReport")
#             os.makedirs(ruta_servicio2, exist_ok=True)  # crear carpeta
#         elif servicios == 3:  # Caso ambos servicios
#             ruta_servicio1 = os.path.join(ruta_carpeta, "cherryCount")
#             ruta_servicio2 = os.path.join(ruta_carpeta, "agroReport")
#             os.makedirs(ruta_servicio1, exist_ok=True)
#             os.makedirs(ruta_servicio2, exist_ok=True)

#         # Campos (cherryCount):
#         for field in fields:
#             ruta_campo = os.path.join(ruta_servicio1, field)
#             os.makedirs(ruta_campo, exist_ok=True)
#             for cuartel in cuarteles:
#                 ruta_cuartel = os.path.join(ruta_campo, cuartel)
#                 os.makedirs(ruta_cuartel, exist_ok=True)

#     except Exception as e:
#         # Caso error
#         print(f"Ocurrió un error: {e}")


def make_path(usuario, fields, ruta):  # Ruta empieza en Dashboard/users
    try:
        ruta_actual = os.path.join(ruta, usuario)  # Dashboard/users/areyes/

        os.makedirs(ruta_actual, exist_ok=True)  # crear carpeta /areyes

        ruta_2 = os.path.join(
            ruta_actual, "cherryCount"
        )  # actualizar directorio: Dashboard/users/areyes/cherryCount
        os.makedirs(ruta_2, exist_ok=True)  # crear carpeta

    except Exception as e:
        # Caso error
        print(f"Ocurrió un error: {e}")
