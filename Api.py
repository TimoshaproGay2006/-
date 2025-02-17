from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
import os
import shutil
import pytesseract
from PIL import Image
import json
from typing import List
import asyncio

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def ocr_image_to_json(image_file):
    try:
        image = Image.open(image_file.file)
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' #<-----
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='rus+eng')

        json_data = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:
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
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/ocr", response_class=HTMLResponse)
async def process_image(request: Request, image: UploadFile = File(...)):
    try:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

        json_data = ocr_image_to_json(image)

        # Сохранение JSON в файл
        json_filename = "output.json"
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        extracted_text = "\n".join([item['text'] for item in json_data])

        return templates.TemplateResponse("index.html", {"request": request, "result": extracted_text, "json_filename": json_filename})

    except HTTPException as e:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": e.detail})

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": f"An unexpected error occurred: {str(e)}"})

@app.get("/output.json", response_class=FileResponse)
async def get_json_file():
    json_filename = "output.json"
    if os.path.exists(json_filename):
        response = FileResponse(json_filename)
        


        asyncio.get_event_loop().call_later(0.1, os.remove, json_filename)
        return response
    else:
        raise HTTPException(status_code=404, detail="JSON file not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
