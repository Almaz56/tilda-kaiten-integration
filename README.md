# Интеграция Tilda с Kaiten

Этот сервис позволяет автоматически создавать задачи в Kaiten при получении заявок из форм Tilda.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Скопируйте файл `.env.example` в `.env` и заполните необходимые переменные окружения:
   - `KAITEN_API_URL` - URL вашего аккаунта Kaiten
   - `KAITEN_API_TOKEN` - API токен Kaiten

## Настройка Tilda

1. В настройках формы Tilda найдите раздел "Интеграции"
2. Добавьте новый вебхук с URL: `https://ваш-домен/webhook/tilda`
3. Выберите метод POST
4. Сохраните настройки

## Запуск

```bash
python main.py
```

Сервис будет доступен по адресу: `http://localhost:8000`

## Настройка на VPS

1. Установите nginx:
```bash
sudo apt update
sudo apt install nginx
```

2. Настройте nginx для проксирования запросов:
```nginx
server {
    listen 80;
    server_name ваш-домен;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Настройте systemd для автоматического запуска:
```bash
sudo nano /etc/systemd/system/tilda-kaiten.service
```

Добавьте следующее содержимое:
```ini
[Unit]
Description=Tilda to Kaiten Integration
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/путь/к/проекту
Environment="PATH=/путь/к/проекту/venv/bin"
ExecStart=/путь/к/проекту/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Запустите сервис:
```bash
sudo systemctl start tilda-kaiten
sudo systemctl enable tilda-kaiten
``` 