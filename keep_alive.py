from fastapi import FastAPI
import uvicorn
from threading import Thread

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
  
def run():
  uvicorn.run(app,host="0.0.0.0",port="5555")
  
def keep_alive():
  t = Thread(target=run)
  t.start()
