from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class TildaWebhook(BaseModel):
    formid: str
    formname: str
    fields: dict

@app.post("/webhook/tilda")
async def tilda_webhook(request: Request):
    data = await request.json()
    
    # Здесь будет логика преобразования данных из Tilda в формат Kaiten
    kaiten_data = {
        "title": f"Новая заявка из формы: {data.get('formname', '')}",
        "description": str(data.get('fields', {})),
        "type": "task",
        "status": "new"
    }
    
    # Отправка данных в Kaiten
    kaiten_api_url = os.getenv("KAITEN_API_URL")
    kaiten_api_token = os.getenv("KAITEN_API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {kaiten_api_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{kaiten_api_url}/api/v1/cards",
        json=kaiten_data,
        headers=headers
    )
    
    return {"status": "success", "kaiten_response": response.json()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 