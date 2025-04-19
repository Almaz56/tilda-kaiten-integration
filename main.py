from fastapi import FastAPI, Request
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/webhook/tilda")
async def tilda_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received data: {data}")
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 