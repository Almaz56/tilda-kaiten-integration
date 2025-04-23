from fastapi import FastAPI, Request, HTTPException
import requests
import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Tilda to Kaiten Integration",
    description="API для интеграции форм Tilda с Kaiten",
    version="1.0.0"
)

@app.post(
    "/webhook/tilda",
    summary="Обработка вебхука от Tilda",
    description="Принимает данные из формы Tilda и создает карточку в Kaiten",
    response_description="Информация о созданной карточке"
)
async def tilda_webhook(request: Request):
    try:
        # Логируем информацию о запросе
        client_host = request.client.host
        headers = dict(request.headers)
        logger.info(f"=== Новый запрос ===")
        logger.info(f"IP клиента: {client_host}")
        logger.info(f"Заголовки запроса: {headers}")
        
        # Получаем тело запроса
        data = await request.json()
        logger.info(f"Полученные данные: {data}")
        
        # Проверка обязательных переменных окружения
        kaiten_api_url = os.getenv("KAITEN_API_URL")
        kaiten_api_token = os.getenv("KAITEN_API_TOKEN")
        kaiten_board_id = os.getenv("KAITEN_BOARD_ID")
        
        logger.info(f"Переменные окружения: KAITEN_API_URL={kaiten_api_url}, KAITEN_BOARD_ID={kaiten_board_id}")
        
        if not all([kaiten_api_url, kaiten_api_token, kaiten_board_id]):
            missing_vars = []
            if not kaiten_api_url: missing_vars.append("KAITEN_API_URL")
            if not kaiten_api_token: missing_vars.append("KAITEN_API_TOKEN")
            if not kaiten_board_id: missing_vars.append("KAITEN_BOARD_ID")
            raise HTTPException(
                status_code=500,
                detail=f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        # Форматирование данных для Kaiten
        fields_text = "\n".join([f"{key}: {value}" for key, value in data.items()])
        kaiten_data = {
            "title": "Новая заявка из формы Tilda",
            "description": f"Данные формы:\n{fields_text}",
            "type": "task",
            "status": "new",
            "board_id": kaiten_board_id
        }
        
        headers = {
            "Authorization": f"Bearer {kaiten_api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Отправка данных в Kaiten: {kaiten_data}")
        logger.info(f"URL запроса: {kaiten_api_url}/api/v1/cards")
        logger.info(f"Заголовки запроса: {headers}")
        
        try:
            response = requests.post(
                f"{kaiten_api_url}/api/v1/cards",
                json=kaiten_data,
                headers=headers
            )
            logger.info(f"Статус ответа от Kaiten: {response.status_code}")
            logger.info(f"Текст ответа от Kaiten: {response.text}")
            response.raise_for_status()  # Проверка на ошибки HTTP
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке данных в Kaiten: {str(e)}")
            logger.error(f"URL запроса: {kaiten_api_url}/api/v1/cards")
            logger.error(f"Заголовки запроса: {headers}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Kaiten: {str(e)}")
        
        response_data = response.json()
        logger.info(f"Ответ от Kaiten: {response_data}")
        logger.info("=== Запрос обработан успешно ===")
        
        return {
            "status": "success",
            "card": {
                "id": response_data.get("id"),
                "title": response_data.get("title"),
                "url": f"{kaiten_api_url}/c/{response_data.get('uid')}"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 