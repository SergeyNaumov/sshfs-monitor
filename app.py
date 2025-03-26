
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from configparser import ConfigParser
import subprocess
import os

app = FastAPI()

# Монтируем папку static для статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Путь к конфигурационному файлу
#CONFIG_FILE = os.path.expanduser("~/Dropbox/my/scripts/sshfs/sshfs_connections.conf")
CONFIG_FILE = "./sshfs_connections.conf"

# Чтение конфигурации
def read_config():
    config = ConfigParser()
    config.read(CONFIG_FILE)
    return config

# Проверка, смонтирована ли точка
def is_mounted(mount_point):
    return os.path.ismount(mount_point)

# Монтирование SSHFS
def mount_sshfs(section):
    config = read_config()
    if section not in config:
        raise HTTPException(status_code=404, detail=f"Соединение {section} не найдено в конфигурации.")

    mount_point = config[section]["mount_point"]
    remote_user = config[section]["remote_user"]
    remote_host = config[section]["remote_host"]
    remote_port = config[section]["remote_port"]
    remote_path = config[section]["remote_path"]
    options = config[section]["options"]

    if is_mounted(mount_point):
        return {"status": "already_mounted", "message": f"{mount_point} уже смонтирована."}

    os.makedirs(mount_point, exist_ok=True)
    command = [
        "sudo", "sshfs",
        "-o", f"ServerAliveInterval=60",
        "-o", "reconnect",
        "-p", remote_port,
        f"{remote_user}@{remote_host}:{remote_path}",
        mount_point,
        "-o", options
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return {"status": "success", "message": f"{mount_point} успешно смонтирована."}
    else:
        raise HTTPException(status_code=500, detail=f"Ошибка монтирования: {result.stderr}")

# Размонтирование SSHFS
def unmount_sshfs(section):
    config = read_config()
    if section not in config:
        raise HTTPException(status_code=404, detail=f"Соединение {section} не найдено в конфигурации.")

    mount_point = config[section]["mount_point"]

    if not is_mounted(mount_point):
        return {"status": "not_mounted", "message": f"{mount_point} не смонтирована."}

    command = ["sudo", "fusermount", "-u", mount_point]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return {"status": "success", "message": f"{mount_point} успешно размонтирована."}
    else:
        raise HTTPException(status_code=500, detail=f"Ошибка размонтирования: {result.stderr}")

# Получение состояния всех соединений (отсортированных)
@app.get("/connections")
def list_connections():
    config = read_config()
    status = {}
    for section in sorted(config.sections()):  # Сортировка по алфавиту
        mount_point = config[section]["mount_point"]
        status[section] = {
            "mount_point": mount_point,
            "mounted": is_mounted(mount_point)
        }
    return status

# Autocomplete: поиск соединений по частичному совпадению
@app.get("/connections/autocomplete")
def autocomplete_connections(query: str):
    config = read_config()
    matches = [section for section in config.sections() if query.lower() in section.lower()]
    return {"matches": sorted(matches)}  # Сортировка результатов по алфавиту

# Маршруты для управления соединениями
@app.post("/connections/{section}/mount")
def mount_connection(section: str):
    return mount_sshfs(section)

@app.post("/connections/{section}/umount")
def unmount_connection(section: str):
    return unmount_sshfs(section)

# Главная страница
@app.get("/")
def read_root():
    return {"message": "Перейдите на /static/index.html для доступа к интерфейсу."}