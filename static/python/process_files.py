from paramiko import SSHClient, AutoAddPolicy
import os
from multiprocessing import Process
from urllib.parse import quote_plus

def run_remote_process(cmd):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostname=str(os.environ["HOST_SSH"]), username=str(os.environ["USER_SSH"]),  password=str(os.environ["PASS_SSH"]))
    stdin, stdout, stderr  = ssh.exec_command(cmd)
    for line in iter(stderr.readline, ""):
        print("[ERR]", line, end="")
    ssh.close()

def process_files(args):
    cmd = (
        "docker exec -e USER='"+quote_plus(os.environ['USER'])+"' -e PASS='"+quote_plus(os.environ['PASS'])+"' -e HOST='"+os.environ['HOST']+"' -i processing_fic bash process_videos.sh "
        + " ".join(args)
    )
    print(cmd) 
    p = Process(target=run_remote_process, args=(cmd,))
    p.start()

"""
def process_files(
    nombre_campo: str,
    tipo_archivo: str,
    extension_archivo: str,
    numero_boletin: str,
    resolucion_ancho: str,
    numero_arboles: str,
    dia_toma_datos: str,
    mesa_toma_datos: str,
    year: str,
    tipo_estructura_fruta: str,
    host_ssh: str, user_ssh: str, pass_ssh: str
) -> None:
    # Your existing file processing logic here

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostname=host_ssh, username=user_ssh, password=pass_ssh)
    stdin, stdout, stderr = ssh.exec_command(
        "docker exec -i processing_fic bash process_videos.sh {} {} {} {} {} {} {} {} {} {}".format(
            nombre_campo,
            tipo_archivo,
            extension_archivo,
            numero_boletin,
            resolucion_ancho,
            numero_arboles,
            dia_toma_datos,
            mesa_toma_datos,
            year,
            tipo_estructura_fruta,
        )
    )
    print("OUTPUT:", stdout.read().decode())
    print("ERROR:", stderr.read().decode())
    ssh.close()
"""


def send_files(
    path_local: str, path_remote: str, host_ssh: str, user_ssh: str, pass_ssh: str
):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostname=host_ssh, username=user_ssh, password=pass_ssh)
    sftp = ssh.open_sftp()
    """ sftp necesita la ruta completa, incluido el nombre del archivo """
    # Extraemos nombre de archivo desde la ruta local
    filename = os.path.basename(path_local)

    # Construir ruta remota completa (directorio + nombre archivo)
    remote_file_path = os.path.join(path_remote, filename).replace("\\", "/")
    print(remote_file_path)
    try:
        sftp.put(path_local, remote_file_path)
    except Exception as e:
        return False

    finally:
        sftp.close()
        ssh.close()


# -------------Funcion con subprocess (antigua) para utilizar decomentar sshpass en dockerfile -------------
# import subprocess


# def send_files(
#     video_path: str,
#     registros_path: str,
#     conteos_path: str,
#     password_ssh: str,
#     # user: str,
#     # field: str,
#     # zone: str,
# ) -> bool:

#     # Opciones de SSH para evitar verificación de host
#     ssh_options = [
#         "-o",
#         "StrictHostKeyChecking=no",
#         "-o",
#         "UserKnownHostsFile=/dev/null",
#     ]
#     # Send images/videos -> file1
#     images = subprocess.run(
#         [
#             "sshpass",
#             "-p",
#             password_ssh,
#             "scp",
#             *ssh_options,
#             video_path,
#             "webFIC@172.16.0.116:/home/webFIC/data/",
#         ],
#     )

#     # Send registros -> file2
#     registros = subprocess.run(
#         [
#             "sshpass",
#             "-p",
#             password_ssh,
#             "scp",
#             *ssh_options,
#             registros_path,
#             "webFIC@172.16.0.116:/home/webFIC/data/metadata/",
#         ],
#     )

#     # Send conteos -> file3
#     conteos = subprocess.run(
#         [
#             "sshpass",
#             "-p",
#             password_ssh,
#             "scp",
#             *ssh_options,
#             conteos_path,
#             "webFIC@172.16.0.116:/home/webFIC/data/counts",
#         ],
#     )
