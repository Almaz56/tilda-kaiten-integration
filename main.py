from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

class TildaWebhook(BaseModel):
    formid: str
    formname: str
    fields: dict

@app.post("/webhook/tilda")
async def tilda_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received data from Tilda: {data}")
        
        # Здесь будет логика преобразования данных из Tilda в формат Kaiten
        kaiten_data = {
            "title": f"Новая заявка из формы: {data.get('formname', '')}",
            "description": str(data.get('fields', {})),
            "type": "task",
            "status": "new",
            "board_id": os.getenv("KAITEN_BOARD_ID")
        }
        
        # Отправка данных в Kaiten
        kaiten_api_url = os.getenv("KAITEN_API_URL")
        kaiten_api_token = os.getenv("KAITEN_API_TOKEN")
        
        logger.info(f"Kaiten API URL: {kaiten_api_url}")
        
        headers = {
            "Authorization": f"Bearer {kaiten_api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Sending data to Kaiten: {kaiten_data}")
        
        response = requests.post(
            f"{kaiten_api_url}/api/v1/cards",
            json=kaiten_data,
            headers=headers
        )
        
        logger.info(f"Kaiten response: {response.status_code} - {response.text}")
        
        return {"status": "success", "kaiten_response": response.json()}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 