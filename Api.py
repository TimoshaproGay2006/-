from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
import os
import shutil
import pytesseract
from PIL import Image
import json
from typing import List

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# templates/index.html
# <!DOCTYPE html>
# <html>
# <head>
#     <title>OCR to JSON</title>
# </head>
# <body>
#     <h1>OCR to JSON</h1>
#     <form action="/ocr" method="post" enctype="multipart/form-data">
#         <label for="image">Upload Image:</label>
#         <input type="file" id="image" name="image" accept="image/*" required><br><br>
#
#         <button type="submit">Process Image</button>
#     </form>
#
#     {% if error_message %}
#         <p style="color: red;">Error: {{ error_message }}</p>
#     {% endif %}
# </body>
# </html>

def ocr_image_to_json(image_file):
    """
    Распознает текст на изображении из UploadFile, возвращает JSON данные.

    Args:
        image_file (UploadFile): Загруженный файл изображения.
    """
    try:
        # Чтение изображения из UploadFile
        image = Image.open(image_file.file)

        # ***Укажите путь к tesseract.exe здесь***
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        # Распознавание текста с указанием языков
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='rus+eng')

        # Формирование JSON структуры
        json_data = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:  # убираем строки без текста
                json_data.append({
                    'text': data['text'][i],
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': data['conf'][i]
                })

        return json_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during OCR: {e}")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ocr", response_class=JSONResponse)
async def process_image(request: Request, image: UploadFile = File(...)):
    """
    Получает изображение, выполняет OCR и возвращает JSON данные.
    """
    try:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

        json_data = ocr_image_to_json(image)  # Вызываем функцию OCR

        return json_data

    except HTTPException as e:
        return JSONResponse(content={"error_message": e.detail}, status_code=e.status_code)

    except Exception as e:
        return JSONResponse(content={"error_message": f"An unexpected error occurred: {str(e)}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)