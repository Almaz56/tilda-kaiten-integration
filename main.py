from fastapi import FastAPI, Request, HTTPException
import requests
import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
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
        data = await request.json()
        logger.info(f"Received data from Tilda: {data}")
        
        # Проверка обязательных переменных окружения
        kaiten_api_url = os.getenv("KAITEN_API_URL")
        kaiten_api_token = os.getenv("KAITEN_API_TOKEN")
        kaiten_board_id = os.getenv("KAITEN_BOARD_ID")
        
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
        
        logger.info(f"Sending data to Kaiten: {kaiten_data}")
        
        try:
            response = requests.post(
                f"{kaiten_api_url}/api/v1/cards",
                json=kaiten_data,
                headers=headers
            )
            response.raise_for_status()  # Проверка на ошибки HTTP
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending data to Kaiten: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Kaiten: {str(e)}")
        
        response_data = response.json()
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
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 