# sshfs-monitor
Для тех, кому надоели проблемы с разрывами при работе с sshfs

# создаём файл sshfs_connections.conf с такими секциями:
[название сервера1]
mount_point=/mnt/[folder_for_mount]
remote_user=[ssh_user]
remote_host=ip_addr
remote_port=port
remote_path=/
options=ServerAliveInterval=60,allow_other,follow_symlinks,transform_symlinks

[название сервера2]
mount_point=/mnt/[folder_for_mount]
remote_user=[ssh_user]
remote_host=ip_addr
remote_port=port
remote_path=/
options=ServerAliveInterval=60,allow_other,follow_symlinks,transform_symlinks

# Создаём env:
python -m venv .venv
pip install fastapi uvicorn configparser aiofiles python-dotenv

# Создаём файл сервиса /etc/systemd/system/sshfs-monitor.service с содержимым:
[Unit]
Description=SSHFS Monitor
After=network-online.target
Wants=network-online.target

[Service]
User=root
Group=root
WorkingDirectory=[путь_к папке с проектом]
Environment="PATH=[__путь к ,venv_]/:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games"
ExecStart=[__путь к ,venv_]/bin/uvicorn app:app --port=8000 --workers 1
Restart=always
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target

# выполняем команды:
systemctl daemon-reload
systemctl enable sshfs-monitor.service
systemctl start sshfs-monitor.service

# сервис будет доступен по адресу:
http://127.0.0.1:8000/static/index.html
