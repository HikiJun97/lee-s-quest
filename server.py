from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import base64
from asyncio import Event
from pydantic import BaseModel

app = FastAPI()
app.mount("/home", StaticFiles(directory="static", html=True), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

update_event = Event()

img_data = ""

class AlertClass(BaseModel):
    img: str
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_page():
    with open("index.html", "r") as f:
        return f.read()

async def stream_image_data():
    while True:
        await update_event.wait()
        # 이미지 파일을 열고 Base64로 인코딩
        with open("image.jpg", "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

        # SSE 형식으로 데이터 전송
        yield f"data: {encoded_image}\n\n"
        update_event.clear()

@app.get("/image-stream")
async def image_stream():
    event_generator = stream_image_data()
    return StreamingResponse(stream_image_data(), media_type="text/event-stream")

@app.post("/update")
async def update_image(img_str: ImgClass):
    global img_data

    update_event.set()
    return {"message": "Image update triggered"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="server:app", host="0.0.0.0", port=9000, reload=True)

