# Importa librerias
from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    session,
    jsonify,
    flash,
    send_file,
    g,
    Response,
)
from config import config
import os
import io
import zipfile
from functools import wraps
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from pathlib import Path
import re
from itsdangerous import URLSafeSerializer, BadSignature
import climate_processing
import math
import random
import requests

# import smtplib

# from email.message import EmailMessage
import pandas as pd
import numpy as np
import subprocess
import datetime
from flask_mail import Mail, Message
import calendar

# Importa database.py

from database import (
    database_login,
    database_add_user,
    database_get_cherry_count_reports,
    database_get_chill_hours_reports,
    database_get_chill_portions_reports,
    database_get_buds_count_reports,
    database_get_users_list,
    database_get_services_list,
    database_get_user_role,
    delete_user,
    database_mod_user,
    database_get_cherry_count_report_info,
    database_get_buds_count_report_info,
    database_add_service,
    database_add_field,
    database_list_user_services,
    database_list_service_fields,
    database_add_user_field,
    turn_notification_off,
    notifications_off,
    list_pending_notifications,
    database_increment_report_id,
    database_get_report_id,
    database_add_agroclimate_report,
    check_duplicated_field,
    check_duplicated_quarter,
    check_user_fields_and_zones,
    database_get_field_coordinates,
    database_get_heat_hours_reports,
    database_get_chill_hours_report_info,
    database_isVerified,
    database_reVerifiedToken
)
from static.python.process_files import process_files, send_files

from static.python.notificationOn import turn_notification_on

from static.python.nameDictionary import (
    translate_to_display_element,
    translate_field_name,
    services_list,
    db_code_to_names,
)

from static.python.passwordStregthCheck import passwordStrengthTest
from report_catalog import list_reports, resolve_relative_pdf

def procesar_multiples_sensores(datos):
   
    sensores = []
    colores = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
        '#9966FF', '#FF9F40', '#FF8A80', '#81C784'
    ]
    
    for idx, (eui, info) in enumerate(datos.items()):
        if len(info) >= 3:
            longitud = info[0]
            latitud = info[1]
            datos_temperatura = info[2]
            
            # Procesar mediciones
            horas = []
            temperaturas = []
            
            for medicion in datos_temperatura:
                if len(medicion) >= 2:
                    fecha_dt = medicion[0]
                    temperatura = medicion[1]
                    
                    # Formato hora:minuto
                    hora_str = fecha_dt.strftime("%H:%M")
                    horas.append(hora_str)
                    temperaturas.append(temperatura)
            
            if temperaturas:  # Solo agregar si hay datos
                sensor = {
                    'eui': eui,
                    'nombre': f"Sensor {idx + 1}",
                    'nombre_corto': eui[-8:],  # Últimos 8 caracteres
                    'color': colores[idx % len(colores)],
                    'color_light': colores[idx % len(colores)] + '20',
                    'latitud': latitud,
                    'longitud': longitud,
                    'horas': horas,
                    'temperaturas': temperaturas,
                    'min_temp': round(min(temperaturas), 2),
                    'max_temp': round(max(temperaturas), 2),
                    'prom_temp': round(sum(temperaturas) / len(temperaturas), 2),
                    'total_registros': len(temperaturas)
                }
                sensores.append(sensor)
    # Encontrar todas las horas únicas para el eje X
    todas_horas = set()
    for sensor in sensores:
        todas_horas.update(sensor['horas'])
    horas_comunes = sorted(list(todas_horas))
    
    return sensores, horas_comunes


def parsed_to_subdata(tus_datos):
    if not tus_datos:
        return pd.DataFrame(), [], {}
    
    todas_las_fechas = set()
    mediciones_por_sensor = {}
    
    for eui, datos_sensor in tus_datos.items():
        if len(datos_sensor) < 3:
            continue
            
        mediciones = datos_sensor[2]
        fechas_sensor = []
        temps_sensor = []
        
        for medicion in mediciones:
            if len(medicion) < 2:
                continue
                
            fecha = medicion[0]
            temp = medicion[1]
            
            if not isinstance(temp, (int, float)):
                continue
            
            # Verificar si es datetime sin usar isinstance directamente
            if hasattr(fecha, 'isoformat') and callable(getattr(fecha, 'isoformat')):
                fecha_iso = fecha.isoformat()
            else:
                try:
                    fecha = pd.to_datetime(fecha)
                    fecha_iso = fecha.isoformat()
                except:
                    continue
            
            fechas_sensor.append(fecha_iso)
            temps_sensor.append(float(temp))
            todas_las_fechas.add(fecha_iso)
        
        if fechas_sensor:
            mediciones_por_sensor[eui] = {
                'fechas': fechas_sensor,
                'temperaturas': temps_sensor
            }
    
    if not mediciones_por_sensor:
        return pd.DataFrame(), [], {}
    
    fechas_ordenadas = sorted(list(todas_las_fechas))
    
    data = {'fecha': fechas_ordenadas}
    
    for eui, sensor_data in mediciones_por_sensor.items():
        temp_dict = dict(zip(sensor_data['fechas'], sensor_data['temperaturas']))
        temps_array = [temp_dict.get(fecha, np.nan) for fecha in fechas_ordenadas]
        data[eui] = temps_array
    
    df = pd.DataFrame(data)
    df.set_index('fecha', inplace=True)
    
    df = df.interpolate(method='linear', limit_direction='both')
    df = df.fillna(method='bfill').fillna(method='ffill')
    
    sensores = list(df.columns)
    
    total_puntos = len(df)
    paso_labels = max(1, total_puntos // 20)
    
    fechas_labels = []
    for i, fecha_str in enumerate(df.index):
        if i % paso_labels == 0 or i == total_puntos - 1:
            try:
                fecha_dt = pd.to_datetime(fecha_str)
                fechas_labels.append(fecha_dt.strftime('%d/%m %H:%M'))
            except:
                fechas_labels.append(fecha_str[5:16])
        else:
            fechas_labels.append('')
    
    metadata = {
        'fechas_completas': df.index.tolist(),
        'fechas_labels': fechas_labels,
        'total_puntos': total_puntos,
        'paso_labels': paso_labels
    }
    
    return df, sensores, metadata

# Define aplicacion
app = Flask(__name__)
bycrypt = Bcrypt(app)
# Key para session handling
app.secret_key = os.environ["FLASKKEY"]


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "cerezas@uoh.cl"
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False


# Creacion de carpeta para subir archivos de conteo
UPLOAD_FOLDER = "/Dashboard/users/upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
DOWNLOAD_FOLDER = "/Dashboard/users/download"
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
ALLOWED_EXTENSIONS = {"zip", "xlsx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crear la carpeta /users

# Consts for send files to process server
app.config["HOST_SSH"] = os.environ["HOST_SSH"]  # IP of the server
app.config["USER_SSH"] = os.environ["USER_SSH"]  # User of the server
app.config["PASS_SSH"] = os.environ["PASS_SSH"]  # Password of the server

mail = Mail(app)


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_valid_email(email):
    return bool(email and EMAIL_REGEX.match(email))


def _get_serializer():
    return URLSafeSerializer(app.secret_key, salt="report-link")


def make_report_token(payload: dict) -> str:
    s = _get_serializer()
    return s.dumps(payload)


def load_report_token(token: str) -> dict | None:
    s = _get_serializer()
    try:
        return s.loads(token)
    except BadSignature:
        return None


def can_view_all_generated_reports() -> bool:
    """Allow catalog-wide inspection for admins or an explicit test account.

    The environment switch is disabled by default and is intended only for a
    controlled test container when an account has no assigned fields.
    """

    if session.get("role") == 0:
        return True
    if session.get("fieldsChillHours"):
        return False
    return os.environ.get("CLIMATE_REPORTS_ALLOW_UNASSIGNED", "false").lower() in {
        "1",
        "true",
        "yes",
    }


# consultando a mongo:
def field_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # funcion para tirarlo pa atras si no tiene algo necesario
        def send_back(bool_service):
            if bool_service:
                return redirect(url_for(services_dict[service_link][1]))
            else:
                return redirect(url_for("home"))

        # obtener servicio desde la ruta (primer segmento), compatible con /<route> y /<route>/<token>
        service_link = request.path.lstrip("/").split("/")[0]

        # parámetros pueden venir como querystring o como token en la URL
        token = None
        if request.view_args and "token" in request.view_args:
            token = request.view_args.get("token")
        params = None
        if token:
            params = load_report_token(token)
            if not params:
                return redirect(url_for("home"))
        else:
            params = {
                "field": request.args.get("field"),
                "zone": request.args.get("zone"),
                "date": request.args.get("date"),
                "name": request.args.get("name"),
                "indate": request.args.get("indate"),
                "outdate": request.args.get("outdate"),
            }

        field = params.get("field")
        zone = params.get("zone")
        date = params.get("date")
        name = params.get("name")
        indate = params.get("indate")
        outdate = params.get("outdate")

        # diccionario link -> servicio, link, fields

        services_dict = {
            "ver_reporte_cherrycount": [
                "cherryCount",
                "conteo_cerezas",
                "fieldsCherryCount",
            ],
            "ver_reporte_chillhours": [
                "cherryChillHours",
                "horas_frio",
                "fieldsChillHours",
            ],
            "ver_reporte_chillportions": [
                "cherryChillPortions",
                "porciones_frio",
                "fieldsChillPortions",
            ],
            "ver_reporte_budscount": [
                "cherryBudsCount",
                "conteo_dardos",
                "fieldsBudsCount",
            ],
            # "ver_reporte_": [
            # "cherryChillPortions",
            # "porciones_frio",
            # "fieldsChillPortions",
            # "home"
            # ],
        }

        # si el endpoint no corresponde a un servicio, tirarlo al home
        if service_link not in services_dict:
            return redirect(url_for("home"))

        # verificar buen formato dl link (pedir todo)
        # si esta mal formatted se tira al home

        match service_link:
            case "ver_reporte_chillhours":
                if not (field and zone and indate and outdate and name):
                    return send_back(bool_service=False)
            case "ver_reporte_chillportions":
                if not (field and zone and indate and outdate and name):
                    return send_back(bool_service=False)
            case "ver_reporte_cherrycount":
                if not (field and zone and date and name):
                    return send_back(bool_service=False)
            case "ver_reporte_budscount":
                if not (field and zone and date and name):
                    return send_back(bool_service=False)
            case _:
                return redirect(url_for("home"))

        # ver si tiene acceso a servicio, campos y zona
        bool_service, bool_fields = check_user_fields_and_zones(
            session["user"], services_dict[service_link][0], field, zone
        )

        if bool_service == False or bool_fields == False:
            return send_back(bool_service)
        # Validation passed: attempt to fetch report data from DB and cache it
        try:
            match services_dict[service_link][0]:
                case "cherryCount":
                    exit_code, report_data = database_get_cherry_count_report_info(
                        field, zone, date, name
                    )
                case "cherryChillHours":
                    exit_code, report_data = database_get_chill_hours_reports(
                        {field: [zone]}
                    )
                case "cherryBudsCount":
                    exit_code, report_data = database_get_buds_count_report_info(
                        field, zone, date, name
                    )
                case "cherryChillPortions":
                    exit_code, report_data = database_get_chill_portions_reports(
                        {field: [zone]}
                    )
                case _:
                    
                    return redirect(url_for("home"))

            if not report_data:
                
                return send_back(bool_service)

            # Cache the validated report data so the view function can reuse it
            g.report_data = report_data
            g.params = params
        except Exception as e:
            print(f"Error fetching report data: {e}")
            return send_back(bool_service)

        # All validation passed; now execute the actual view function
        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function

def deny_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return redirect(url_for("home"))
    return decorated_function

def cherry_count_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session["cherryCount"]:
            return redirect(url_for("conteo_cerezas"))
        return f(*args, **kwargs)

    return decorated_function


def buds_count_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session["cherryBudsCount"]:
            return redirect(url_for("conteo_dardos"))
        return f(*args, **kwargs)

    return decorated_function


def chill_hours_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session["cherryChillHours"]:
            return redirect(url_for("horas_frio"))
        return f(*args, **kwargs)

    return decorated_function


def chill_portions_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session["cherryChillPortions"]:
            return redirect(url_for("porciones_frio"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ("user" not in session) or (session["role"] != 0):
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return decorated_function


def noc_admin_required(f):
    """Protect the NOC while keeping its own container authentication-free.

    The website is the public entry point, so authentication and authorization
    are enforced here before any request is forwarded to the internal NOC
    service.  The NOC API is read-only and is never exposed directly.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if NOC_ADMIN_ONLY and session.get("role") != 0:
            return "Forbidden", 403
        return f(*args, **kwargs)

    return decorated_function


NOC_UPSTREAM_URL = os.environ.get("NOC_UPSTREAM_URL", "http://127.0.0.1:8060").rstrip("/")
NOC_ADMIN_ONLY = os.environ.get("NOC_ADMIN_ONLY", "true").strip().lower() not in {
    "0", "false", "no", "off"
}


@app.route("/noc", defaults={"noc_path": ""}, methods=["GET"])
@app.route("/noc/", defaults={"noc_path": ""}, methods=["GET"])
@app.route("/noc/<path:noc_path>", methods=["GET"])
@noc_admin_required
def noc_proxy(noc_path):
    """Forward the authenticated NOC page/API/assets to the internal service."""
    target = f"{NOC_UPSTREAM_URL}/{noc_path}" if noc_path else f"{NOC_UPSTREAM_URL}/"
    try:
        upstream = requests.get(
            target,
            params=request.args,
            headers={"Accept": request.headers.get("Accept", "*/*")},
            timeout=30,
        )
    except requests.RequestException as error:
        return f"NOC service unavailable: {error}", 502

    hop_by_hop = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"}
    headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in hop_by_hop
    }
    return Response(upstream.content, status=upstream.status_code, headers=headers)


# Root
@app.route("/")
def index():
    # Redirecciona a login
    return redirect(url_for("login"))


# Vista de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mail = request.form["email"]
        password = request.form["password"]
        login_status, session_data = database_login(bycrypt, mail, password)
        if session_data == {}:
            flash("Correo electrónico o contraseña incorrectos.")
            return render_template("login.html", email=mail)
        if session_data["verified"]==False:
            return redirect(url_for("noverified",mail=mail))
        if login_status == 0:
            session["user"] = mail
            session["role"] = session_data["role"]
            session["name"] = session_data["name"]
            session["cherryCount"] = session_data["cherryCount"]
            session["cherryBudsCount"] = session_data["cherryBudsCount"]
            session["cherryChillHours"] = session_data["cherryChillHours"]
            session["fieldsCherryCount"] = session_data["fieldsCherryCount"]
            session["fieldsBudsCount"] = session_data["fieldsBudsCount"]
            session["fieldsChillHours"] = session_data["fieldsChillHours"]
            return redirect(url_for("home"))
    else:
        return render_template("login.html", email="")

def randomtoken(l):
    token = ""
    chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    for i in range(l):
        token += random.choice(chars)
    return token


def verification_mail(to,token):
    title = "[Cerezas UOH] Verificación de email"
    sender="Cerezas UOH <cerezas@uoh.cl>"
    recipient = [to]
    verification_url = f"https://cerezas.uoh.cl/verification?tk={token}"
    html_body = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="es">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Verificación de email</title>
        </head>
        <body style="margin:0; padding:0; background-color:#f5f5f5; -webkit-text-size-adjust:none; -ms-text-size-adjust:none;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#f5f5f5;">
                <tr>
                    <td align="center" style="padding:40px 10px;">
                        <table border="0" cellpadding="0" cellspacing="0" width="600" style="max-width:600px; width:100%; background-color:#ffffff; border-radius:8px;">
                            
                            <!-- LOGO -->
                            <tr>
                                <td align="center" style="padding:40px 30px 20px 30px;">
                                    <img src="cid:logo_uoh" alt="UOH Cerezas" width="200" style="display:block; border:0; outline:none; text-decoration:none; -ms-interpolation-mode:bicubic; width:200px; max-width:100%;" />
                                </td>
                            </tr>
                            
                            <!-- TEXTO -->
                            <tr>
                                <td style="padding:20px 40px; text-align:center; font-family:Arial, Helvetica, sans-serif; font-size:16px; line-height:1.6; color:#333333;">
                                    <p style="margin:0 0 15px 0;"><strong>Hola!</strong></p>
                                    <p style="margin:0 0 25px 0;">Gracias por registrarte. Para completar tu verificación, haz clic en el botón:</p>
                                </td>
                            </tr>
                            
                           
                            <tr>
                                <td align="center" style="padding:10px 40px 30px 40px;">
                                    <table border="0" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center" bgcolor="#871d0a" style="background-color:#871d0a; border-radius:6px;">
                                                <a href="{verification_url}" target="_blank" style="display:inline-block; padding:16px 40px; font-family:Arial, Helvetica, sans-serif; font-size:16px; font-weight:bold; color:#ffffff; text-decoration:none; border-radius:6px; border:1px solid #871d0a;">
                                                    Verificar mi cuenta
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            
                            
                            <tr>
                                <td style="padding:0 40px 30px 40px; text-align:center; font-family:Arial, Helvetica, sans-serif; font-size:13px; line-height:1.5; color:#666666;">
                                    <p style="margin:0 0 8px 0;">Si el botón no funciona, copia este enlace:</p>
                                    <p style="margin:0; word-break:break-all;">
                                        <a href="{verification_url}" style="color:#871d0a; text-decoration:underline;">{verification_url}</a>
                                    </p>
                                </td>
                            </tr>
                            
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>"""
    
    # Versión texto plano para clientes que no soportan HTML
    text_body = f"""
    Cerezas UOH - Verificación de email
    Su link de verificación es:
    {verification_url}
    Si no puede hacer clic en el enlace, copie y péguelo en su navegador.
    """
    msg = Message(
        subject=title,
        body=text_body,
        html=html_body,
        sender=sender,
        recipients=recipient,
    )
    with open("static/images/UOHCerezas.jpg", "rb") as fp:
        msg.attach(
            filename="UOHGanaderia.png",
            content_type="image/png",
            data=fp.read(),
            disposition="inline",
            headers={"Content-ID": "<logo_uoh>"}
        )
        
    mail.send(msg)


# Vista de signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        mail = request.form["email"]
        password = request.form["password"]
        tk = randomtoken(15)
        signup_status, utils = database_add_user(bycrypt, name, mail, password,[False],1,tk)
        
        if signup_status == 0 and utils == False:
            verification_mail(mail,tk)
            return redirect(url_for("signed"))
        if signup_status == 0 and utils == True:
            flash("Correo electrónico en uso. Pruebe uno diferente.")
            return render_template("signup.html", email=mail)
        else:
            flash("Error. Intente nuevamente.")
            return render_template("signup.html", email=mail)
        
    else:
        return render_template("signup.html", email="")

@app.route("/signed", methods=["GET", "POST"])
def signed():
    return render_template("signed.html")

@app.route("/noverified", methods=["GET", "POST"])
def noverified():
    if request.method == "POST":
        mail = request.args.get("mail")
        ec, tk = database_reVerifiedToken(mail)
        verification_mail(mail,tk)
        return redirect(url_for("signed"))
    else:
        return render_template("noverified.html")

@app.route("/verification", methods=["GET"])
def verification():
    try:
        r_code = database_isVerified(request.args.get('tk'))
        if r_code == 2:
            text = "El link ha expirado. Registrese nuevamente."
        if r_code == 1:
            text = "Su cuenta a sido verificada correctamente."
        else:
            text = "Ha ocurrido un error, intente nuevamente."
    except:
        text = "Ha ocurrido un error, intente nuevamente."
    return render_template("verification.html",text=text)

@app.route("/home")
@login_required
def home():
    print(session)
    if session["role"] == 0:
        return render_template(
            "home.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            notifications_list=list_pending_notifications(session["user"]),
        )
    else:
        return render_template(
            "home.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            notifications_list=list_pending_notifications(session["user"]),
        )


@app.route("/conteo_cerezas")
@login_required
def conteo_cerezas():
    if session["role"] == 0:
        return render_template(
            "conteo_cerezas.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )
    else:
        return render_template(
            "conteo_cerezas.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )


@app.route("/contacto")
@login_required
def contacto():
    if session["role"] == 0:
        return render_template(
            "contacto.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )
    else:
        return render_template(
            "contacto.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )

@app.route("/contacto_externo")
def contacto_externo():
    return render_template(
            "contacto_externo.html"
    )
 

@app.route("/contacto2", methods=["GET"])
def contacto2():
    return render_template("contacto2.html")


@app.route("/mail", methods=["GET", "POST"])
def send_mail():
    # Simulate sending an email

    if request.method == "POST":
        title = request.form["title"]
        email = request.form["email"]
        mensaje = request.form["mensaje"]
        recipent = os.environ["CONTACT"].split()
        msg = Message(f"{title}",body=f"Email: {email}\nMensaje: {mensaje}",sender=("FIC WebApp", email),reply_to=email, recipients=recipent)
        mail.send(msg)
        return render_template("send_mail.html")
    else:
        return redirect(url_for("contacto"))


# Vista de upload_cherrycount
@app.route("/upload_cherrycount", methods=["GET", "POST"])
@login_required
@cherry_count_required
def upload_cherrycount():
    if request.method == "POST":
        uploaded_files = []
        name = session["name"]
        folderpath = Path(
            app.config["UPLOAD_FOLDER"],
            name,
            "cherryCount",
            request.form["select-field"],
            request.form["select-zone"],
        )

        folderpath.mkdir(parents=True, exist_ok=True)

        database_increment_report_id("cherryCount", request.form["select-field"])

        exit_code, r_id = database_get_report_id(
            "cherryCount", request.form["select-field"]
        )
        files_names = ["file1", "file2", "file3"]
        data_date = datetime.datetime.strptime(
            request.form["text-dia-datos"], "%Y-%m-%d"
        ).date()
        for file in files_names:
            if file in request.files and request.files[file].filename != "":
                if file == "file1":
                    filename = secure_filename(
                        "images_"
                        + request.form["select-field"]
                        + "_R"
                        + str(r_id)
                        + "_cherries.zip"
                    )
                elif file == "file2":
                    filename = secure_filename(
                        "Registro_" + request.form["select-field"] + str(r_id) + ".xlsx"
                    )
                else:
                    filename = secure_filename(
                        "Conteos_referencia_"
                        + request.form["select-field"]
                        + str(r_id)
                        + ".xlsx"
                    )

                file_requested = request.files[file]
                filepath = Path(
                    app.config["UPLOAD_FOLDER"],
                    name,
                    "cherryCount",
                    request.form["select-field"],
                    request.form["select-zone"],
                    filename,
                )
                file_requested.save(os.path.join(filepath))
                uploaded_files.append(filepath)

        if len(uploaded_files) == 3:
            # Send video
            send_files(
                str(uploaded_files[0]),
                "/home/webFIC/data/",
                app.config["HOST_SSH"],
                app.config["USER_SSH"],
                app.config["PASS_SSH"],
            )
            # Send registro
            send_files(
                str(uploaded_files[1]),
                "/home/webFIC/data/metadata/",
                app.config["HOST_SSH"],
                app.config["USER_SSH"],
                app.config["PASS_SSH"],
            )
            # Send conteo
            send_files(
                str(uploaded_files[2]),
                "/home/webFIC/data/counts",
                app.config["HOST_SSH"],
                app.config["USER_SSH"],
                app.config["PASS_SSH"],
            )

            process_files(
                [
                    request.form["select-field"],
                    request.form["select-type-file"],
                    request.form["select-extension-file"],
                    str(r_id),  # session["id_boletin"]
                    request.form["text-res-ancho"],
                    request.form["text-num-arboles"],
                    str(data_date.day),
                    str(data_date.month),
                    str(data_date.year),
                    "cherries",
                ]
            )
            # Borrar archivos subidos
            for p in uploaded_files:
                try:
                    Path(p).unlink(missing_ok=True)
                except Exception as e:
                    app.logger.warning(f"No se pudo borrar {p}: {e}")

            # Devolver respuesta JSON para AJAX
            if (
                request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.accept_mimetypes.accept_json
            ):
                return (
                    jsonify(
                        {"success": True, "message": "Archivos enviados correctamente"}
                    ),
                    200,
                )

            return redirect(url_for("upload_cherrycount"))
        else:
            # Devolver error JSON para AJAX
            if (
                request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.accept_mimetypes.accept_json
            ):
                return (
                    jsonify(
                        {"success": False, "message": "Error en la subida de archivos"}
                    ),
                    400,
                )

            return redirect(url_for("upload_cherrycount"))

    else:
        if session["fieldsCherryCount"]:
            field_names = []
            for f in session["fieldsCherryCount"]:
                f_name = f[f.find("-") + 1 :]
                f_name = f_name.replace("-", " ")
                field_names.append(f_name.capitalize())
            named_fields = [field_names, list(session["fieldsCherryCount"].keys())]
        else:
            named_fields = [[], []]
        if session["role"] == 0:
            return render_template(
                "upload_cherrycount.html",
                show_admin_tab=True,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )
        else:
            return render_template(
                "upload_cherrycount.html",
                show_admin_tab=False,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )


@app.route("/upload_budscount", methods=["GET", "POST"])
@login_required
@buds_count_required
def upload_budscount():
    if request.method == "POST":
        uploaded_files = []
        name = session["name"]
        folderpath = Path(
            app.config["UPLOAD_FOLDER"],
            name,
            "budsCount",
            request.form["select-field"],
            request.form["select-zone"],
        )

        folderpath.mkdir(parents=True, exist_ok=True)

        database_increment_report_id("budsCount", request.form["select-field"])

        exit_code, r_id = database_get_report_id(
            "budsCount", request.form["select-field"]
        )
        if exit_code != 0 or r_id is None:
            # Responder en JSON si es una solicitud AJAX
            if (
                request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.accept_mimetypes.accept_json
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "No se pudo obtener ID de reporte",
                        }
                    ),
                    400,
                )

            flash("Error al obtener ID de reporte, reintentar")
            return redirect(url_for("upload_budscount"))

        files_names = ["file1", "file2", "file3"]
        data_date = datetime.datetime.strptime(
            request.form["text-dia-datos"], "%Y-%m-%d"
        ).date()
        for file in files_names:
            if file in request.files and request.files[file].filename != "":
                if file == "file1":
                    filename = secure_filename(
                        "images_"
                        + request.form["select-field"]
                        + "_R"
                        + str(r_id)
                        + "_buds.zip"
                    )
                elif file == "file2":
                    filename = secure_filename(
                        "Registro_" + request.form["select-field"] + str(r_id) + ".xlsx"
                    )
                else:
                    filename = secure_filename(
                        "Conteos_referencia_"
                        + request.form["select-field"]
                        + str(r_id)
                        + ".xlsx"
                    )

                file_requested = request.files[file]
                filepath = Path(
                    app.config["UPLOAD_FOLDER"],
                    name,
                    "budsCount",
                    request.form["select-field"],
                    request.form["select-zone"],
                    filename,
                )
                file_requested.save(os.path.join(filepath))
                uploaded_files.append(filepath)

        if len(uploaded_files) == 3:
            # Send video
            send_files(
                str(uploaded_files[0]),
                "/home/webFIC/data/",
                app.config["HOST_SSH"],
                app.config["USER_SSH"],
                app.config["PASS_SSH"],
            )
            # Send registro
            send_files(
                str(uploaded_files[1]),
                "/home/webFIC/data/metadata/",
                app.config["HOST_SSH"],
                app.config["USER_SSH"],
                app.config["PASS_SSH"],
            )
            # Send conteo
            send_files(
                str(uploaded_files[2]),
                "/home/webFIC/data/counts",
                app.config["HOST_SSH"],
                app.config["USER_SSH"],
                app.config["PASS_SSH"],
            )

            process_files(
                [
                    request.form["select-field"],
                    request.form["select-type-file"],
                    request.form["select-extension-file"],
                    str(r_id),  # id boletin
                    request.form["text-res-ancho"],
                    request.form["text-num-arboles"],
                    str(data_date.day),
                    str(data_date.month),
                    str(data_date.year),
                    "buds",
                ]
            )
            for p in uploaded_files:
                try:
                    Path(p).unlink(missing_ok=True)
                except Exception as e:
                    app.logger.warning(f"No se pudo borrar {p}: {e}")
            # Devolver respuesta JSON para AJAX
            if (
                request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.accept_mimetypes.accept_json
            ):
                return (
                    jsonify(
                        {"success": True, "message": "Archivos enviados correctamente"}
                    ),
                    200,
                )

            return redirect(url_for("upload_budscount"))
        else:
            # Devolver error JSON para AJAX
            if (
                request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.accept_mimetypes.accept_json
            ):
                return (
                    jsonify(
                        {"success": False, "message": "Error en la subida de archivos"}
                    ),
                    400,
                )

            # flash(f"Error en la subido de archivo, reintentar")
            return redirect(url_for("upload_budscount"))

    else:
        if session["fieldsBudsCount"]:
            field_names = []
            for f in session["fieldsBudsCount"]:
                f_name = f[f.find("-") + 1 :]
                f_name = f_name.replace("-", " ")
                field_names.append(f_name.capitalize())
            named_fields = [field_names, list(session["fieldsBudsCount"].keys())]
        else:
            named_fields = [[], []]

        if session["role"] == 0:
            return render_template(
                "upload_budscount.html",
                show_admin_tab=True,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )
        else:
            return render_template(
                "upload_budscount.html",
                show_admin_tab=False,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )


# Vista de Metodología de Procesamiento.
@app.route("/metodologia")
@login_required
def metodologia():
    if session["role"] == 0:
        return render_template(
            "metodologia.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )
    else:
        return render_template(
            "metodologia.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )


# Vista de Reportes Disponibles
@app.route("/reportes_cherrycount")
@login_required
def reportes():
    exit_code, field_data = database_get_cherry_count_reports(
        session["fieldsCherryCount"]
    )

    for i in field_data:
        i.pop("_id", None)
        try:
            i["token"] = make_report_token(
                {
                    "service": "cherryCount",
                    "field": i.get("field"),
                    "zone": str(i.get("zone")),
                    "date": str(i.get("date")),
                    "name": str(i.get("name")),
                }
            )
        except Exception:
            pass

    if session["role"] == 0:
        return render_template(
            "conteo_cerezas_reportes.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryCount", session["user"]),
        )
    else:
        return render_template(
            "conteo_cerezas_reportes.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryCount", session["user"]),
        )


@app.route("/reportes_budscount")
@login_required
def reportes_buds():
    exit_code, field_data = database_get_buds_count_reports(session["fieldsBudsCount"])
    for i in field_data:
        i.pop("_id", None)
        try:
            i["token"] = make_report_token(
                {
                    "service": "cherryBudsCount",
                    "field": i.get("field"),
                    "zone": str(i.get("zone")),
                    "date": str(i.get("date")),
                    "name": str(i.get("name")),
                }
            )
        except Exception:
            pass
    if session["role"] == 0:
        return render_template(
            "conteo_dardos_reportes.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryBudsCount", session["user"]),
        )
    else:
        return render_template(
            "conteo_dardos_reportes.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryBudsCount", session["user"]),
        )


@app.route("/reportes_chillhours")
@login_required
def reportes_chillhours():
    user_fields = session.get("fieldsChillHours") or {}
    is_admin = can_view_all_generated_reports()
    # Administrators can inspect the complete read-only catalog. Regular users
    # remain restricted to the fields assigned to their profile.
    authorized_sites = None if is_admin else user_fields.keys()
    # MongoDB is consulted only to enrich an already-generated catalog entry
    # with the existing report number and zone. A database failure must not
    # hide the read-only PDF catalog.
    metadata_by_period = {}
    try:
        metadata_fields = user_fields
        if is_admin:
            metadata_fields = {report["site"]: {} for report in list_reports(None)}
        _, metadata_rows = database_get_chill_hours_reports(metadata_fields)
        for metadata in metadata_rows or []:
            key = (
                metadata.get("data-field"),
                metadata.get("kind"),
                str(metadata.get("in-date")),
                str(metadata.get("out-date")),
            )
            metadata_by_period[key] = metadata
    except Exception:
        metadata_by_period = {}
    field_data = []
    for report in list_reports(authorized_sites):
        metadata = metadata_by_period.get(
            (
                report["site"],
                report["kind"],
                str(report["in-date"]),
                str(report["out-date"]),
            ),
            {},
        )
        if metadata.get("name") is not None:
            report["name"] = str(metadata["name"])
        if metadata.get("zone") is not None:
            report["zone"] = str(metadata["zone"])
        report["token"] = make_report_token(
            {
                "service": "generatedClimateReport",
                "site": report["site"],
                "kind": report["kind"],
                "report_date": report["report_date"],
                "relative_path": report["relative_path"],
            }
        )
        report["download_url"] = url_for("download_generated_report", token=report["token"])
        report["view_url"] = url_for("view_generated_report", token=report["token"])
        field_data.append(report)
    if session["role"] == 0:
        return render_template(
            "horas_frio_reportes.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryChillHours", session["user"]),
        )
    else:
        return render_template(
            "horas_frio_reportes.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryChillHours", session["user"]),
        )

@app.route("/reportes_heathours")
@deny_access
@login_required
def reportes_heathours():
    exit_code, field_data = database_get_heat_hours_reports(
        session["fieldsHeatHours"]
    )

    for i in field_data:
        i.pop("_id", None)
        try:
            i["token"] = make_report_token(
                {
                    "service": "cherryHeatHours",
                    "field": i.get("data-field"),
                    "zone": str(i.get("zone")),
                    "indate": str(i.get("in-date")),
                    "outdate": str(i.get("out-date")),
                    "name": str(i.get("name")),
                }
            )
        except Exception:
            pass
   
    if session["role"] == 0:
        return render_template(
            "horas_calor_reportes.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryHeatHours", session["user"]),
        )
    else:
        return render_template(
            "horas_calor_reportes.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryHeatHours", session["user"]),
        )
    
@app.route("/reportes_chillportions")
@login_required
@deny_access
def reportes_chillportions():
    exit_code, field_data = database_get_chill_portions_reports(
        session["fieldsChillPortions"]
    )

    for i in field_data:
        i.pop("_id", None)
        try:
            i["token"] = make_report_token(
                {
                    "service": "cherryChillPortions",
                    "field": i.get("data-field"),
                    "zone": str(i.get("zone")),
                    "indate": str(i.get("in-date")),
                    "outdate": str(i.get("out-date")),
                    "name": str(i.get("name")),
                }
            )
        except Exception:
            pass

    if session["role"] == 0:
        return render_template(
            "porciones_frio_reportes.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryChillPortions", session["user"]),
        )
    else:
        return render_template(
            "porciones_frio_reportes.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            reports=field_data,
            notifications=notifications_off("cherryChillPortions", session["user"]),
        )


# Vista de Reporte Seleccionado
# http://localhost:8050/ver_reporte_cherrycount?field=fic2-graneros-agrofurore&zone=4&date=1764374400&name=17
@app.route("/ver_reporte_cherrycount")
@app.route("/ver_reporte_cherrycount/<token>")
@login_required
@field_required
def ver_reporte(token=None):
    from flask import g

    # Reuse report_data cached by @field_required decorator to avoid duplicate DB call
    report_data = getattr(g, "report_data", None)
    if not report_data:
        # Fallback: should not happen if decorator works correctly
        exit_code, report_data = database_get_cherry_count_report_info(
            (getattr(g, "params", {}) or {}).get("field") or request.args.get("field"),
            (getattr(g, "params", {}) or {}).get("zone") or request.args.get("zone"),
            (getattr(g, "params", {}) or {}).get("date") or request.args.get("date"),
            (getattr(g, "params", {}) or {}).get("name") or request.args.get("name"),
        )
        if exit_code != 0 or not report_data:
            return redirect(url_for("home"))

    n_report = report_data["name"]
    data_field = report_data["data-field"]
    date = report_data["date"]
    date = datetime.datetime.fromtimestamp(int(date))
    day = str(date.day)
    month = str(date.month)
    year = str(date.year)
    n_trees = report_data["n_trees"]
    df_excel = pd.DataFrame.from_dict(report_data["data"])
    # df_excel.rename(columns={
    #     'breed': 'Variedad',
    #     'field' : 'Cuartel',
    #     'name': 'Planta',
    #     'zone': 'Zona',
    #     'ripe': 'Roja',
    #     'unripe': 'Naranja',
    #     'greens': 'Verde',
    #     'counts': 'Estimados',
    #     'pos': 'Pos',
    #     'counts_lower': 'Estimados min',
    #     'counts_upper': 'Estimados max',
    #     'maturity': 'Madurez'
    # })
    # Renombra las columnas recibidas de las bases de datos
    df_excel.columns = [
        "Variedad",
        "Cuartel",
        "Planta",
        "Zona",
        "Roja",
        "Naranja",
        "Verde",
        "Estimados",
        "Pos",
        "Estimados min",
        "Estimados max",
        "Madurez",
    ]
    # Reordena las columnas
    df_excel = df_excel.iloc[:, [1, 3, 0, 2, 4, 5, 6, 11, 7, 10, 9, 8]]
    cherry_mean = df_excel.loc[:, "Estimados"].mean()
    trees_len = len(df_excel)
    name = session["name"]
    folderpath = Path(
        app.config["DOWNLOAD_FOLDER"],
        name,
        "cherryCount",
        (getattr(g, "params", {}) or {}).get("field") or request.args.get("field"),
        (getattr(g, "params", {}) or {}).get("zone") or request.args.get("zone"),
        (getattr(g, "params", {}) or {}).get("date") or request.args.get("date"),
        (getattr(g, "params", {}) or {}).get("name") or request.args.get("name"),
    )

    folderpath.mkdir(parents=True, exist_ok=True)
    excel_path = Path(folderpath, "reporte_cerezas.xlsx")
    df_excel.to_excel(excel_path, index=False)
    excel_url = url_for("download_excel", path=str(excel_path))
    image_path = Path(folderpath, data_field + ".jpeg")
    script_path = Path("static/python/write_pdf.py")
    pdf_path = Path(folderpath, "reporte_cerezas.pdf")
    loc_matrix = df_excel[["Planta", "Pos"]].values.tolist()
    subprocess.run(
        [
            "python3",
            str(script_path),
            "--path-predictions",
            str(excel_path),
            "--path-save",
            str(pdf_path),
            "--data-field",
            data_field,
            "--day",
            day,
            "--month",
            month,
            "--year",
            year,
            "--n-report",
            n_report,
            "--n-trees",
            str(n_trees),
            "--type-data",
            "cherries",
        ]
    )
    pdf_url = url_for("download_pdf", path=str(pdf_path))
    report_dict = df_excel.to_dict(orient="records")
    if session["role"] == 0:
        return render_template(
            "ver_reporte_cherrycount.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            excel_path=excel_url,
            pdf_path=pdf_url,
            image=image_path,
            report_dict=report_dict,
            report_name=n_report,
            field_name=translate_field_name(data_field),
            year=year,
            month=month,
            day=day,
            n_trees=n_trees,
            cherry_mean=round(cherry_mean, 1),
            loc_matrix=loc_matrix,
        )
    else:
        return render_template(
            "ver_reporte_cherrycount.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            excel_path=excel_url,
            pdf_path=pdf_url,
            image=image_path,
            report_dict=report_dict,
            report_name=n_report,
            field_name=translate_field_name(data_field),
            year=year,
            month=month,
            day=day,
            n_trees=n_trees,
            cherry_mean=round(cherry_mean, 1),
            loc_matrix=loc_matrix,
        )


@app.route("/ver_reporte_budscount")
@app.route("/ver_reporte_budscount/<token>")
@login_required
@field_required
def ver_reporte_buds(token=None):
    from flask import g

    # Reuse report_data cached by @field_required decorator to avoid duplicate DB call
    report_data = getattr(g, "report_data", None)
    if not report_data:
        # Fallback: should not happen if decorator works correctly
        exit_code, report_data = database_get_buds_count_report_info(
            (getattr(g, "params", {}) or {}).get("field") or request.args.get("field"),
            (getattr(g, "params", {}) or {}).get("zone") or request.args.get("zone"),
            (getattr(g, "params", {}) or {}).get("date") or request.args.get("date"),
            (getattr(g, "params", {}) or {}).get("name") or request.args.get("name"),
        )
        if exit_code != 0 or not report_data:
            
            return redirect(url_for("home"))

    n_report = report_data["name"]
    data_field = report_data["data-field"]
    date = report_data["date"]
    date = datetime.datetime.fromtimestamp(int(date))
    day = str(date.day)
    month = str(date.month)
    year = str(date.year)
    n_trees = report_data["n_trees"]
    df_excel = pd.DataFrame.from_dict(report_data["data"])

    # Renombra las columnas recibidas de las bases de datos
    df_excel = df_excel.rename(
        columns={
            "breed": "Variedad",
            "field": "Cuartel",
            "name": "Planta",
            "zone": "Zona",
            "yemas": "Yemas",
            "dardos": "Dardos",
            "hojas": "Hojas",
            "flores": "Flores",
            "counts": "Estimados",
            "counts_lower": "Estimados min",
            "counts_upper": "Estimados max",
            "pos": "Pos",
            "maturity": "Madurez",
        }
    )[
        [
            "Cuartel",
            "Zona",
            "Variedad",
            "Planta",
            "Yemas",
            "Dardos",
            "Hojas",
            "Flores",
            "Madurez",
            "Estimados",
            "Estimados max",
            "Estimados min",
            "Pos",
        ]
    ]

    buds_mean = df_excel.loc[:, "Estimados"].mean()
    trees_len = len(df_excel)
    name = session["name"]
    folderpath = Path(
        app.config["DOWNLOAD_FOLDER"],
        name,
        "budsCount",
        (getattr(g, "params", {}) or {}).get("field") or request.args.get("field"),
        (getattr(g, "params", {}) or {}).get("zone") or request.args.get("zone"),
        (getattr(g, "params", {}) or {}).get("date") or request.args.get("date"),
        (getattr(g, "params", {}) or {}).get("name") or request.args.get("name"),
    )

    folderpath.mkdir(parents=True, exist_ok=True)
    excel_path = Path(folderpath, "reporte_buds.xlsx")
    df_excel.to_excel(excel_path, index=False)
    excel_url = url_for("download_excel", path=str(excel_path))
    image_path = Path(folderpath, data_field + ".jpeg")
    script_path = Path("static/python/write_pdf.py")
    pdf_path = Path(folderpath, "reporte_buds.pdf")
    loc_matrix = df_excel[["Planta", "Pos"]].values.tolist()

    subprocess.run(
        [
            "python3",
            str(script_path),
            "--path-predictions",
            str(excel_path),
            "--path-save",
            str(pdf_path),
            "--data-field",
            data_field,
            "--day",
            day,
            "--month",
            month,
            "--year",
            year,
            "--n-report",
            n_report,
            "--n-trees",
            str(n_trees),
            "--type-data",
            "buds",
        ]
    )
    pdf_url = url_for("download_pdf", path=str(pdf_path))
    report_dict = df_excel.to_dict(orient="records")
    if session["role"] == 0:
        return render_template(
            "ver_reporte_budscount.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            excel_path=excel_url,
            pdf_path=pdf_url,
            image=image_path,
            report_dict=report_dict,
            report_name=n_report,
            field_name=translate_field_name(data_field),
            year=year,
            month=month,
            day=day,
            n_trees=n_trees,
            buds_mean=round(buds_mean, 1),
            loc_matrix=loc_matrix,
        )
    else:
        return render_template(
            "ver_reporte_budscount.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            excel_path=excel_url,
            pdf_path=pdf_url,
            image=image_path,
            report_dict=report_dict,
            report_name=n_report,
            field_name=translate_field_name(data_field),
            year=year,
            month=month,
            day=day,
            n_trees=n_trees,
            buds_mean=round(buds_mean, 1),
            loc_matrix=loc_matrix,
        )


@app.route("/ver_reporte_chillhours")
@app.route("/ver_reporte_chillhours/<token>")
@login_required
@field_required
def ver_reporte_chillhours(token=None):
    params = getattr(g, "params", {}) or {}
    data_field = params.get("field") or request.args.get("field")
    zone = params.get("zone") or request.args.get("zone")
    in_date = params.get("indate") or request.args.get("indate")
    out_date = params.get("outdate") or request.args.get("outdate")
    report_name = params.get("name") or request.args.get("name")  # ID del reporte
    user_name = session["name"]  # Nombre del usuario para la carpeta
    tipo = params.get("tipo") or request.args.get("tipo")
    parsed_date_in = datetime.datetime.fromtimestamp(int(in_date))
    inday = str(parsed_date_in.day)
    inmonth = str(parsed_date_in.month)
    inyear = str(parsed_date_in.year)
    indate_l = [inday, inmonth, inyear]
    parsed_date_out = datetime.datetime.fromtimestamp(int(out_date))
    outday = str(parsed_date_out.day)
    outmonth = str(parsed_date_out.month)
    outyear = str(parsed_date_out.year)
    outdate_l = [outday, outmonth, outyear]
   
    #get sensor data
    data = database_get_chill_hours_report_info(data_field,zone,int(in_date),int(out_date))[1]
    parsed_data = dict()
    for element in range(len(data)):
        if data[element]["sensor_device_id"] in parsed_data:
            try:
                fecha_dt = datetime.datetime.strptime(data[element]["time_sensor_tx"], "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                fecha_dt = datetime.datetime.strptime(data[element]["time_sensor_tx"], "%Y-%m-%dT%H:%M:%SZ")
            parsed_data[data[element]["sensor_device_id"]][2].append([fecha_dt,float(data[element]["payload_decoded"]["TempC_SHT"])])
        else:
            parsed_data[data[element]["sensor_device_id"]] = [data[element]["sensor_static_data"]["sensor_lat"],data[element]["sensor_static_data"]["sensor_lon"],[]]
            try:
                fecha_dt = datetime.datetime.strptime(data[element]["time_sensor_tx"], "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                fecha_dt = datetime.datetime.strptime(data[element]["time_sensor_tx"], "%Y-%m-%dT%H:%M:%SZ")
            parsed_data[data[element]["sensor_device_id"]][2].append([fecha_dt,float(data[element]["payload_decoded"]["TempC_SHT"])])
    
    #GET AL DATES IN THE INTERVAL YEAR _ MONTH _ DAY _ HOUR INTs
    years = []
    months = []
    days = []   
    hours = []
    for y in range(parsed_date_in.year,parsed_date_out.year+1):
        start_month = 1
        end_month = 12
        if y == parsed_date_in.year:
            start_month = parsed_date_in.month
        if y == parsed_date_out.year:
            end_month = parsed_date_out.month
        
        for m in range(start_month,end_month+1):
            start_day = 1
            end_day = 31
            if m in [4,6,9,11]:
                end_day = 30
            elif m == 2:
                if calendar.isleap(y):
                    end_day = 29
                else:
                    end_day = 28
            if y == parsed_date_in.year and m == parsed_date_in.month:
                start_day = parsed_date_in.day
            if y == parsed_date_out.year and m == parsed_date_out.month:
                end_day = parsed_date_out.day
            
            for d in range(start_day,end_day+1):
                start_hour = 1
                end_hour = 24
                if y == parsed_date_in.year and m == parsed_date_in.month and d == parsed_date_in.day:
                    start_day = parsed_date_in.day
                if y == parsed_date_out.year and m == parsed_date_out.month and d == parsed_date_out.day:
                    end_day = parsed_date_out.day
                
                for h in range(start_hour,end_hour+1):
                    years.append(y)
                    months.append(m)
                    days.append(d)
                    hours.append(h)

    #GENERATE DATAFRAME WITH DATES
    sensor_nulos = {}
    
    for k in parsed_data.keys():
        sensor_nulos[k] = np.full(len(years), np.nan, dtype=float)
    dataframe = pd.DataFrame({'year':years,'month':months,'day':days,'hour':hours} | sensor_nulos)
    #Retorna dict {SENSOR : [LAT,LON,HOURS,TEMPERATURES]} | SET DATA INTO DATAFRAME np.where pandas
    def accumulateHours(parsed_data,dataframe):
        for sensor in parsed_data:
            counter = 0
            hour = None
            temperature = 0
            aux_date = None
            for data in parsed_data[sensor][2]:
                if hour == None:
                    aux_date = data[0]
                    hour = data[0].hour
                    temperature += data[1]
                    counter += 1
                elif hour == data[0].hour:
                    aux_date = data[0]
                    temperature += data[1]
                    counter += 1
                else: 
                    #REPLACE TEMPERATURE IN DF
                    mask = (dataframe['year'] == aux_date.year) & \
                        (dataframe['month'] == aux_date.month) & \
                        (dataframe['day'] == aux_date.day) & \
                        (dataframe['hour'] == aux_date.hour)

                    dataframe.loc[mask, sensor] = temperature/counter

                    aux_date = data[0]
                    hour = data[0].hour
                    counter = 0
                    temperature = 0
                    temperature += data[1]
                    counter += 1
            dataframe[sensor] = dataframe[sensor].interpolate(method='spline', order=3,limit_area='inside')
    
    accumulateHours(parsed_data, dataframe)
    to_be_proc = dataframe.drop(['year','month','day','hour'],axis=1)
    
    sensores = []
    portions_cold, cold_units, cold_hours = climate_processing.get_yearly_cold_stats(to_be_proc,to_be_proc.columns)
    colores = [
       '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
        '#9966FF', '#FF9F40', '#FF8A80', '#81C784'
    ]   
    for i,eui in enumerate(cold_hours.keys()):
        temperaturas = dataframe[eui].round(2).tolist()
        sensor = {
                        'eui': eui,
                        'nombre': f"Sensor {i + 1}",
                        'nombre_corto': eui[-8:],  # Últimos 8 caracteres
                        'color': colores[i % len(colores)],
                        'color_light': colores[i % len(colores)] + '20',
                        'latitud': parsed_data[eui][0],
                        'longitud': parsed_data[eui][1],
                        'temperaturas': temperaturas,
                        'horas_frio':cold_hours[eui].tolist(),
                        'porciones_frio':portions_cold[eui].tolist(),
                    }
        sensores.append(sensor)

    folderpath = Path(
        app.config["DOWNLOAD_FOLDER"],
        user_name,  # Usar nombre del usuario, no el ID del reporte
        "chillHours",
        data_field,
        zone,
        in_date,
        out_date,
    )

    folderpath.mkdir(parents=True, exist_ok=True)

    script_path = Path("static/python/write_agroclimate_pdf.py")
    pdf_path = Path(folderpath, "reporte_horas_frio.pdf")

    # Generar PDF
    subprocess.run(
        [
            "python3",
            str(script_path),
            "--path-save",
            str(pdf_path),
            "--data-field",
            data_field,
            "--zone",
            zone,
            "--day-in",
            inday,
            "--month-in",
            inmonth,
            "--year-in",
            inyear,
            "--day-out",
            outday,
            "--month-out",
            outmonth,
            "--year-out",
            outyear,
            "--n-report",
            report_name,
            "--type-data",
            "chillhours",
        ]
    )

    pdf_url = url_for("download_pdf", path=str(pdf_path))
    
    # Obtener coordenadas del campo desde la base de datos
    location = database_get_field_coordinates(data_field)
    
    horas = pd.to_datetime(dataframe[['year', 'month', 'day', 'hour']]).dt.strftime('%Y-%m-%dT%H:%M:%S').tolist()

    mean_temp = []
    mean_chillh = []
    mean_chillp = []

    def is_valid_value(val):
        if val is None:
            return False
        if isinstance(val, float) and math.isnan(val):
            return False
        if val == "" or val == "None" or val == "null":
            return False
        return True

    for i in range(len(horas)):
        h_temp = 0
        c_temp = 0
        h_chillh = 0
        c_chillh = 0
        h_chillp = 0
        c_chillp = 0
        
        for sensor in sensores:
            if is_valid_value(sensor['temperaturas'][i]):
                h_temp += sensor['temperaturas'][i]
                c_temp += 1
            
            if is_valid_value(sensor['horas_frio'][i]):
                h_chillh += sensor['horas_frio'][i]
                c_chillh += 1
            
            if is_valid_value(sensor['porciones_frio'][i]):
                h_chillp += sensor['porciones_frio'][i]
                c_chillp += 1
        
        mean_temp.append(h_temp / c_temp if c_temp > 0 else None)
        mean_chillh.append(h_chillh / c_chillh if c_chillh > 0 else None)
        mean_chillp.append(h_chillp / c_chillp if c_chillp > 0 else None)


    table_data = pd.DataFrame({'horas':horas,'temperaturas':mean_temp,'horas_frio':mean_chillh,'porciones_frio':mean_chillp})

    if tipo == 'Diario':
        table_data['temperaturas'] = table_data['temperaturas'].round(1)
        table_data['temperaturas'] = table_data['temperaturas'].fillna('Sin datos')
        table_data['horas'] = table_data['horas'].str.replace('T', ' - ')
        table_data['horas_frio'] = table_data['horas_frio'].round(2)
        table_data['porciones_frio'] = table_data['porciones_frio'].round(2)    
    else:
        table_data['fecha'] = table_data['horas'].str[:10]
        grouped = table_data.groupby('fecha').agg({
            'temperaturas': 'mean',
            'horas_frio': 'last',
            'porciones_frio': 'last'
        }).reset_index()
        
        grouped['horas'] = grouped['fecha'] 
        grouped = grouped.drop(columns=['fecha'])
        
        grouped['temperaturas'] = grouped['temperaturas'].round(1)
        grouped['temperaturas'] = grouped['temperaturas'].fillna('Sin datos')
        grouped['horas_frio'] = grouped['horas_frio'].round(2)
        grouped['porciones_frio'] = grouped['porciones_frio'].round(2)
        
        table_data = grouped
    table_data = table_data.to_dict(orient='records')
    
    if session["role"] == 0:
        return render_template(
            "ver_reporte_chillhours.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            pdf_path=pdf_url,
            report_name=report_name,
            field_name=translate_field_name(data_field),
            indate=indate_l,
            outdate=outdate_l,
            loc=location,
            tipo=tipo,
            sensores=sensores,
            horas=horas,
            tabledata = table_data
        )
    else:
        return render_template(
            "ver_reporte_chillhours.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            pdf_path=pdf_url,
            report_name=report_name,
            field_name=translate_field_name(data_field),
            indate=indate_l,
            outdate=outdate_l,
            location=location,
            tipo=tipo,
            sensores=sensores,
            horas=horas,
            tabledata = table_data
        )


@app.route("/ver_reporte_chillportions")
@app.route("/ver_reporte_chillportions/<token>")
@login_required
@deny_access
@field_required
def ver_reporte_chillportions(token=None):
    params = getattr(g, "params", {}) or {}
    data_field = params.get("field") or request.args.get("field")
    zone = params.get("zone") or request.args.get("zone")
    in_date = params.get("indate") or request.args.get("indate")
    out_date = params.get("outdate") or request.args.get("outdate")
    name = params.get("name") or request.args.get("name")

    parsed_date_in = datetime.datetime.fromtimestamp(int(in_date))
    inday = str(parsed_date_in.day)
    inmonth = str(parsed_date_in.month)
    inyear = str(parsed_date_in.year)
    indate_l = [inday, inmonth, inyear]

    parsed_date_out = datetime.datetime.fromtimestamp(int(out_date))
    outday = str(parsed_date_out.day)
    outmonth = str(parsed_date_out.month)
    outyear = str(parsed_date_out.year)
    outdate_l = [outday, outmonth, outyear]

    """
    df_excel.columns = [
        "Variedad",
        "Cuartel",
        "Planta",
        "Zona",
        "Roja",
        "Naranja",
        "Verde",
        "Estimados",
        "Pos",
        "Estimados min",
        "Estimados max",
        "Madurez",
    ]
    df_excel = df_excel.iloc[:, [1, 3, 0, 2, 4, 5, 6, 11, 7, 10, 9, 8]]
    cherry_mean = df_excel.loc[:, "Estimados"].mean()
    trees_len = len(df_excel)
    name = session["name"]
    """
    user_name = session["name"]  # Nombre del usuario para la carpeta
    report_name = name  # ID del reporte

    folderpath = Path(
        app.config["DOWNLOAD_FOLDER"],
        user_name,
        "chillPortions",
        data_field,
        zone,
        in_date,
        out_date,
    )

    folderpath.mkdir(parents=True, exist_ok=True)

    script_path = Path("static/python/write_agroclimate_pdf.py")
    pdf_path = Path(folderpath, "reporte_porciones_frio.pdf")

    # Generar PDF
    subprocess.run(
        [
            "python3",
            str(script_path),
            "--path-save",
            str(pdf_path),
            "--data-field",
            data_field,
            "--zone",
            zone,
            "--day-in",
            inday,
            "--month-in",
            inmonth,
            "--year-in",
            inyear,
            "--day-out",
            outday,
            "--month-out",
            outmonth,
            "--year-out",
            outyear,
            "--n-report",
            report_name,
            "--type-data",
            "chillportions",
        ]
    )

    pdf_url = url_for("download_pdf", path=str(pdf_path))
    
    # Obtener coordenadas del campo desde la base de datos
    location = database_get_field_coordinates(data_field)

    
    
    if session["role"] == 0:
        return render_template(
            "ver_reporte_chillportions.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            pdf_path=pdf_url,
            report_name=report_name,
            field_name=translate_field_name(data_field),
            indate=indate_l,
            outdate=outdate_l,
            location=location,
            
        )
    else:
        return render_template(
            "ver_reporte_chillportions.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
            pdf_path=pdf_url,
            report_name=report_name,
            field_name=translate_field_name(data_field),
            indate=indate_l,
            outdate=outdate_l,
            location=location,
            
        )


@app.route("/gestion_usuarios", methods=["GET", "POST"])
@admin_required
def gestion_usuarios():
    if request.method == "POST":
        form_name = request.form.get("form_name")
        # Add user
        if form_name == "add_user":
            try:
                name = request.form["name-input"]
                email = request.form["email-input"]
                password = request.form["password-input"]
                services = request.form.getlist("addService")
                role = request.form["addRole"]
                list_of_services = services_list()
                service_list = [s[0] in services for s in list_of_services]
                admin_mail = request.form["email-input-add"]
                admin_password = request.form["password-input-add"]
                
                login_status, session_data = database_login(
                    bycrypt, admin_mail, admin_password
                )
               
                if login_status == 0:
                    if session_data.get("role") == 0:
                        login_status, existed = database_add_user(
                            bycrypt, name, email, password, service_list, role
                        )
                        if login_status == 0 and not existed:
                            flash(f"Usuario {email} creado correctamente.")
                            return redirect(url_for("gestion_usuarios"))
                        elif login_status == 0 and existed:
                            flash(
                                f'Por favor, elija otro correo electrónico, "{email}" ya está asociado a un usuario.'
                            )

                            # return redirect(url_for("gestion_usuarios"))
                            return "", 204
                        else:
                            flash("Error al crear usuario.")
                            return redirect(url_for("gestion_usuarios"))
                    else:
                        flash("Error: Usuario sin permisos de administrador.")
                        return redirect(url_for("gestion_usuarios"))
                else:
                    flash("Error: Correo y/o contraseña de administrador incorrectos.")
                    return redirect(url_for("gestion_usuarios"))
            except Exception as e:
                flash(f"Error al procesar la solicitud de creación de usuario:\n {e}")
                return redirect(url_for("gestion_usuarios"))

        # Delete user
        elif form_name == "del_user":
            try:
                # Nombres de campos según la plantilla: emailadmin-input, email-input, password-input
                user_email = request.form["selectedUser-del"]
                mail = request.form["email-input"]
                password = request.form["password-input"]
                login_status, session_data = database_login(bycrypt, mail, password)
                # si contraseña correcta y el usuario es ADMIN
                if login_status == 0:
                    if session_data.get("role") == 0:
                        deleted_count = delete_user(user_email)
                        if deleted_count > 0:
                            flash(f"Usuario {user_email} eliminado correctamente.")
                            return redirect(url_for("gestion_usuarios"))
                        else:
                            flash(
                                "No se pudo eliminar el usuario. Usuario inexistente."
                            )
                            return redirect(url_for("gestion_usuarios"))
                    else:
                        flash("ERROR: Usuario sin permisos de administrador.")
                        return redirect(url_for("gestion_usuarios"))
                else:
                    flash("ERROR: Correo y/o contraseña incorrectos.")
                    return redirect(url_for("gestion_usuarios"))
            except Exception as e:
                flash(f"Error al procesar la solicitud de eliminación:\n {e}")
                return redirect(url_for("gestion_usuarios"))

        # Modify user (renders list for selection)
        elif form_name == "mod_user":
            try:
                mail = request.form["email-input-mod"]
                password = request.form["password-input-mod"]
                s_mail = request.form["selectedUser"]
                new_services = request.form.getlist("modService")
                new_role = request.form["modRole"]
                list_of_services = services_list()
                service_list = [s[0] in new_services for s in list_of_services]

                login_status, session_data = database_login(bycrypt, mail, password)
                # login_status = database_mod_user(s_mail,service_list, new_role)
                a_users = database_get_users_list()
                if login_status == 0:
                    if session["role"] == 0:
                        moded_users = database_mod_user(s_mail, service_list, new_role)
                        if moded_users > -1:
                            flash(f"Usuario {s_mail} modificado correctamente.")
                            return redirect(url_for("gestion_usuarios"))
                        else:
                            flash(
                                "No se pudo modificar el usuario. Usuario inexistente."
                            )
                            return redirect(url_for("gestion_usuarios"))
                    else:
                        flash("ERROR: Usuario sin permisos de administrador.")
                        return redirect(url_for("gestion_usuarios"))
                else:
                    flash("ERROR: Correo y/o contraseña de administrador incorrectos.")
                    return redirect(url_for("gestion_usuarios"))
            except Exception as e:
                flash(f"Error al procesar la solicitud de modificación:\n {e}")
                return redirect(url_for("gestion_usuarios"))
    else:
        # GET
        if session["role"] == 0:
            return render_template(
                "gestion_usuarios.html",
                show_admin_tab=True,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                all_users=database_get_users_list()[1],
                all_services=services_list(),
            )
        else:
            return render_template(
                "gestion_usuarios.html",
                show_admin_tab=False,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
            )


@app.route("/gestion_servicios", methods=["GET", "POST"])
@admin_required
def gestion_servicios():
    if request.method == "POST":
        form_name = request.form.get("form_name")
        # Add service
        if form_name == "add_service":
            try:
                db_name = request.form["name-input"]
                f_name = request.form["field-input"]
                admin_mail = request.form["email-input-service"]
                admin_password = request.form["password-input-service"]
                login_status, session_data = database_login(
                    bycrypt, admin_mail, admin_password
                )
                if login_status == 0:
                    if session_data.get("role") == 0:
                        login_status, existed = database_add_service(db_name, f_name)
                        if login_status == 0 and not existed:
                            flash(f'Servicio "{db_name}" creado correctamente.')
                            return redirect(url_for("gestion_servicios"))
                        elif login_status == 0 and existed:
                            flash(
                                f'Elije otro nombre, ya hay un servicio con el nombre "{db_name}".'
                            )
                            return redirect(url_for("gestion_servicios"))
                        else:
                            flash("Error al crear servicio.")
                            return redirect(url_for("gestion_servicios"))
                    else:
                        flash("ERROR: Usuario sin permisos de administrador.")
                        return redirect(url_for("gestion_servicios"))
                else:
                    flash("ERROR: Correo y/o contraseña de administrador incorrectos.")
                    return redirect(url_for("gestion_servicios"))
            except Exception as e:
                flash(f"Error al procesar la solicitud de creación de servicio:\n {e}")
                return redirect(url_for("gestion_servicios"))

        # Add field
        elif form_name == "add_field":
            try:
                mail = request.form["email-input"]
                password = request.form["password-input"]
                s_service = request.form["selectedService"]
                f_name = request.form["field-input"]
                login_status, session_data = database_login(bycrypt, mail, password)
                if login_status == 0:
                    if session["role"] == 0:
                        added_fields, existed = database_add_field(s_service, f_name)
                        if added_fields == 0 and not existed:
                            flash(
                                f'Campo "{f_name}" añadido al servicio "{s_service}" correctamente.'
                            )
                            return redirect(url_for("gestion_servicios"))
                        elif added_fields == 0 and existed:
                            flash(
                                f'Elija otro nombre para el campo, "{f_name}" ya está en uso en el servicio "{s_service}".'
                            )
                            return redirect(url_for("gestion_servicios"))
                        else:
                            flash("Error al crear campo.")
                            return redirect(url_for("gestion_servicios"))
                    else:
                        flash("ERROR: Usuario sin permisos de administrador.")
                        return redirect(url_for("gestion_servicios"))
                else:
                    flash("ERROR: Correo y/o contraseña de administrador incorrectos.")
                    return redirect(url_for("gestion_servicios"))
            except Exception as e:
                flash(f"Error al procesar la solicitud de creación de campo:\n {e}")
                return redirect(url_for("gestion_servicios"))

        # Add fields to user
        elif form_name == "add_user_field":
            try:
                # Admin credentials
                mail = request.form["email-input"]
                password = request.form["password-input"]
                # User data
                s_mail = request.form["selected-user"]
                s_service = request.form["selected-service"]
                field_to_add = request.form["selected-field"]
                quarter_n = request.form["quarter-input"]

                login_status, session_data = database_login(bycrypt, mail, password)

                if login_status == 0:
                    if session["role"] == 0:
                        added_fields, existed = database_add_user_field(
                            s_service, field_to_add, s_mail, quarter_n
                        )
                        if added_fields == 0 and not existed:
                            flash(
                                f'Campo "{translate_field_name(field_to_add)}" con cuartel {quarter_n} añadido al servicio "{s_service}" del usuario "{s_mail}" correctamente.'
                            )
                            return redirect(url_for("gestion_servicios"))
                        elif added_fields == 0 and existed:
                            flash(
                                f'El usuario "{s_mail}" ya tiene el cuartel {quarter_n} del campo "{translate_field_name(field_to_add)}" en el servicio "{translate_to_display_element(s_service)}".'
                            )
                            return redirect(url_for("gestion_servicios"))
                        else:
                            flash("Error al agregar el campo.")
                            return redirect(url_for("gestion_servicios"))
                    else:
                        flash("ERROR: Usuario sin permisos de administrador.")
                        return redirect(url_for("gestion_servicios"))
                else:
                    flash("ERROR: Correo y/o contraseña de administrador incorrectos.")
                    return redirect(url_for("gestion_servicios"))
            except Exception as e:
                flash(f"Error al procesar la solicitud de adición de campo:\n {e}")
                return redirect(url_for("gestion_servicios"))
    else:
        # GET
        dbs = []
        for code in database_get_services_list():
            dbs.append([code,db_code_to_names(code)])
        if session["role"] == 0:
            return render_template(
                "gestion_servicios.html",
                show_admin_tab=True,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                all_users=database_get_users_list()[1],
                all_dbs=dbs,
            )
        else:
            return render_template(
                "gestion_servicios.html",
                show_admin_tab=False,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
            )


@app.route("/conteo_dardos")
@login_required
def conteo_dardos():
    if session["role"] == 0:
        return render_template(
            "conteo_dardos.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )
    else:
        return render_template(
            "conteo_dardos.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )


@app.route("/horas_frio")
@login_required
def horas_frio():
    if session["role"] == 0:
        return render_template(
            "horas_frio.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            disable_generate=False,
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )
    else:
        return render_template(
            "horas_frio.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            disable_generate=False,
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            name=session["name"],
        )


@app.route("/porciones_frio")
@login_required
def porciones_frio():
    if session["role"] == 0:
        return render_template(
            "porciones_frio.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            disable_generate=False,
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            show_portions_tab=session["cherryChillPortions"],
            name=session["name"],
        )
    else:
        return render_template(
            "porciones_frio.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            disable_generate=False,
            show_cherrycount_tab=session["cherryCount"],
            show_budscount_tab=session["cherryBudsCount"],
            show_portions_tab=session["cherryChillPortions"],
            name=session["name"],
        )


@app.route("/horas_calor")
@login_required
def horas_calor():
    if session["role"] == 0:
        return render_template(
            "horas_calor.html",
            show_admin_tab=True,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            disable_generate=False,
            show_budscount_tab=session["cherryBudsCount"],
            show_portions_tab=session["cherryChillPortions"],
            name=session["name"],
        )
    else:
        return render_template(
            "horas_calor.html",
            show_admin_tab=False,
            show_chill_tab=session["cherryChillHours"],
            show_cherrycount_tab=session["cherryCount"],
            disable_generate=False,
            show_budscount_tab=session["cherryBudsCount"],
            show_portions_tab=session["cherryChillPortions"],
            name=session["name"],
        )


@app.route("/logout")
@login_required
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/get_zones_cherrycount", methods=["POST"])
@login_required
def get_zones_cherrycount():
    field = request.json.get("field")
    zones = session["fieldsCherryCount"][field]
    return jsonify(zones)

@app.route("/get_zones_budscount", methods=["POST"])
@login_required
def get_zones_budscount():
    field = request.json.get("field")
    zones = session["fieldsBudsCount"][field]
    return jsonify(zones)



@app.route("/get_zones_chillportions", methods=["POST"])
@login_required
def get_zones_chillportions():
    field = request.json.get("field")
    zones = session["fieldsChillPortions"][field]
    return jsonify(zones)


@app.route("/get_zones_chillhours", methods=["POST"])
@login_required
def get_zones_chillhours():
    field = request.json.get("field")
    zones = session["fieldsChillHours"][field]
    return jsonify(zones)


@app.route("/get_user_services", methods=["POST"])
@login_required
def get_user_services():
    user = request.json.get("user")
    services = database_list_user_services(
        user
    )  # [ [display_name, name], [display_name, name] ]
    new_services = []
    for s in range(len(services)):
        if services[s][1]=="cherryChillHours":
            new_services.append(["Reportes Agroclimáticos",services[s][1]])
        elif services[s][1]=="cherryHeatHours" or services[s][1]=="cherryChillPortions":
            continue
        else:
            new_services.append([services[s][0],services[s][1]])

    return jsonify(new_services)


# /get_user_role
@app.route("/get_user_role", methods=["POST"])
@login_required
def get_user_role():
    user = request.json.get("user")
    role = database_get_user_role(user)
    return jsonify(role)


# Validate admin credentials
@app.route("/login_admin_validation", methods=["POST"])
@login_required
def login_admin_validation():
    data = request.get_json()
    mail = data.get("mail")
    password = data.get("password")
    login_status, session_data = database_login(bycrypt, mail, password)
    if login_status == 0:
        if session_data.get("role") == 0:
            return jsonify(0)
    else:
        return jsonify(1)


# Prevent duplicated users
@app.route("/checkDuplicates", methods=["POST"])
@login_required
def checkDuplicates():
    data = request.json.get("input")
    users_list = database_get_users_list()[1]
    if data in users_list:
        return jsonify(1)
    elif data not in users_list:
        return jsonify(0)


# Prevent duplicated services
@app.route("/checkDuplicatedService", methods=["POST"])
@login_required
def checkDuplicatedService():
    data = request.json.get("input")
    services_list = database_get_services_list()
    services_list.extend(["config", "admin", "local", "FIC_CEREZAS_WEB"])
    if data in services_list:
        return jsonify(1)
    elif data not in services_list:
        return jsonify(0)


# Prevent duplicated fields
@app.route("/checkDuplicatedField", methods=["POST"])
@login_required
def checkDuplicatedField():
    data = request.get_json()
    service = data.get("service")
    field = data.get("field")
    exists = check_duplicated_field(
        service, field
    )  # [ [display_name, name], [display_name, name] ]
    if exists:
        return jsonify(1)
    return jsonify(0)


# Prevent duplicated quarters
@app.route("/checkDuplicatedQuarter", methods=["POST"])
@login_required
def checkDuplicatedQuarter():
    data = request.get_json()
    mail = data.get("mail")
    service = data.get("service")
    field = data.get("field")
    quarter = data.get("quarter")
    exists = check_duplicated_quarter(mail, service, field, int(quarter))
    if exists:
        return jsonify(1)
    return jsonify(0)


@app.route("/get_service_fields", methods=["POST"])
@login_required
def get_service_fields():
    service = request.json.get("service")
    fields = database_list_service_fields(
        service
    )  # [ [display_name, name], [display_name, name] ]
    print(fields)
    return jsonify(fields)


@app.route("/passwordStrength", methods=["POST"])
@login_required
def passwordStrength():
    pwrd = request.json.get("value")
    isStrong = passwordStrengthTest(f"{pwrd}")  # 0: not strong, 1: strong enough
    if isStrong:
        return jsonify(1)
    elif not isStrong:
        return jsonify(0)


@app.route("/process_notification", methods=["POST"])
@login_required
def process_notification():
    data = request.get_json()
    value = data.get("value", {})
    service = value.get("service")
    fields_list = value.get("fields_list")
    url = turn_notification_off(service, fields_list)

    return jsonify({"status": "ok", "redirect": url})


@app.route("/download_excel")
@login_required
def download_excel():
    path = request.args.get("path")
    return send_file(path, as_attachment=True)


@app.route("/download_pdf")
@login_required
def download_pdf():
    path = request.args.get("path")
    return send_file(path, as_attachment=True)


def _resolve_generated_report(token):
    """Resolve a signed catalog token to an authorized existing PDF."""

    payload = load_report_token(token)
    if not payload or payload.get("service") != "generatedClimateReport":
        raise LookupError("invalid report token")
    authorized_sites = (session.get("fieldsChillHours") or {}).keys()
    is_admin = can_view_all_generated_reports()
    if not is_admin and payload.get("site") not in authorized_sites:
        raise PermissionError("unauthorized report")
    catalog_sites = None if is_admin else authorized_sites
    catalog_paths = {
        report["relative_path"]
        for report in list_reports(catalog_sites)
        if report["site"] == payload.get("site")
        and report["kind"] == payload.get("kind")
        and report["report_date"] == payload.get("report_date")
    }
    if payload.get("relative_path") not in catalog_paths:
        raise LookupError("report is not in the current catalog")
    path = resolve_relative_pdf(payload.get("relative_path"))
    if path is None:
        raise LookupError("report file not found")
    return path, payload


@app.route("/view_generated_report/<token>")
@login_required
def view_generated_report(token):
    """Open an existing PDF inline in the browser."""

    try:
        path, _ = _resolve_generated_report(token)
    except PermissionError:
        return "Reporte no autorizado", 403
    except LookupError:
        return "Reporte no encontrado", 404
    return send_file(path, as_attachment=False, mimetype="application/pdf", download_name=path.name)


@app.route("/download_generated_report/<token>")
@login_required
def download_generated_report(token):
    """Download one existing pipeline PDF as an attachment."""

    try:
        path, _ = _resolve_generated_report(token)
    except PermissionError:
        return "Reporte no autorizado", 403
    except LookupError:
        return "Reporte no encontrado", 404
    return send_file(path, as_attachment=True, download_name=path.name)


@app.route("/download_generated_reports", methods=["POST"])
@login_required
def download_generated_reports():
    """Download the selected existing PDFs as a ZIP archive."""

    payload = request.get_json(silent=True) or {}
    tokens = payload.get("tokens")
    if not isinstance(tokens, list) or not tokens:
        return jsonify({"error": "No hay reportes seleccionados"}), 400
    if len(tokens) > 500:
        return jsonify({"error": "Demasiados reportes seleccionados"}), 400

    reports = []
    seen = set()
    try:
        for token in tokens:
            path, report = _resolve_generated_report(token)
            if report["relative_path"] in seen:
                continue
            seen.add(report["relative_path"])
            reports.append((path, report))
    except PermissionError:
        return jsonify({"error": "Reporte no autorizado"}), 403
    except LookupError:
        return jsonify({"error": "Uno de los reportes ya no está disponible"}), 404

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for path, report in reports:
            arcname = "/".join(
                [report["site"], report["kind"], report["report_date"], path.name]
            )
            zip_file.write(path, arcname=arcname)
    archive.seek(0)
    filename = f"climate-reports-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    return send_file(archive, mimetype="application/zip", as_attachment=True, download_name=filename)


@app.route("/images/<path:filepath>")
@login_required
def get_image(filepath):
    file_path = Path("/") / filepath if not filepath.startswith("/") else Path(filepath)
    return send_file(file_path)


@app.route("/upload_chillhours", methods=["GET", "POST"])
@login_required
@deny_access
@chill_hours_required
def upload_chillhours():
    if request.method == "POST":
        uploaded_files = []
        name = session["name"]
        database_increment_report_id("cherryChillHours", request.form["select-field"])
        exit_code, r_id = database_get_report_id(
            "cherryChillHours", request.form["select-field"]
        )
        turn_notification_on("cherryChillHours", request.form["select-field"])

        database_add_agroclimate_report(
            "FIC_CEREZAS_HORAS_FRIO",
            request.form["select-field"],
            request.form["select-zone"],
            request.form["fechaInicio"],
            request.form["fechaFin"],
            str(r_id),
        )
        # Responder en JSON si es una solicitud AJAX
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.accept_mimetypes.accept_json
        ):
            return jsonify({"success": True, "message": "Solicitud registrada"}), 200

        # Fallback
        return redirect(url_for("horas_frio"))

    else:
        if session["fieldsChillHours"]:
            field_names = []
            for f in session["fieldsChillHours"]:
                f_name = f[f.find("-") + 1 :]
                f_name = f_name.replace("-", " ")
                field_names.append(f_name.capitalize())
            named_fields = [field_names, list(session["fieldsChillHours"].keys())]
        else:
            named_fields = [[], []]
        if session["role"] == 0:
            return render_template(
                "upload_chillhours.html",
                show_admin_tab=True,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )
        else:
            return render_template(
                "upload_chillhours.html",
                show_admin_tab=False,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )


@app.route("/upload_chillportions", methods=["GET", "POST"])
@login_required
@deny_access
@chill_portions_required
def upload_chillportions():
    if request.method == "POST":
        uploaded_files = []
        name = session["name"]
        database_increment_report_id(
            "cherryChillPortions", request.form["select-field"]
        )
        exit_code, r_id = database_get_report_id(
            "cherryChillPortions", request.form["select-field"]
        )
        turn_notification_on("cherryChillPortions", request.form["select-field"])

        database_add_agroclimate_report(
            "FIC_CEREZAS_PORCIONES_FRIO",
            request.form["select-field"],
            request.form["select-zone"],
            request.form["fechaInicio"],
            request.form["fechaFin"],
            str(r_id),
        )
        # Responder en JSON si es una solicitud AJAX
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.accept_mimetypes.accept_json
        ):
            return jsonify({"success": True, "message": "Solicitud registrada"}), 200

        # mensaje de que ya se solicitó!
        return redirect(url_for("porciones_frio"))

    else:
        if session["fieldsChillPortions"]:
            field_names = []
            for f in session["fieldsChillPortions"]:
                f_name = f[f.find("-") + 1 :]
                f_name = f_name.replace("-", " ")
                field_names.append(f_name.capitalize())
            named_fields = [field_names, list(session["fieldsChillPortions"].keys())]
        else:
            named_fields = [[], []]
        if session["role"] == 0:
            return render_template(
                "upload_chillportions.html",
                show_admin_tab=True,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )
        else:
            return render_template(
                "upload_chillportions.html",
                show_admin_tab=False,
                show_chill_tab=session["cherryChillHours"],
                show_cherrycount_tab=session["cherryCount"],
                show_budscount_tab=session["cherryBudsCount"],
                name=session["name"],
                fields=named_fields,
            )


# Main, ejecuta la app
if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.run(host="0.0.0.0", port=8050, debug=True)
