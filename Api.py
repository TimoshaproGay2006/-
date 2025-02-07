from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
import os
import shutil
import pytesseract
from PIL import Image
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def ocr_image_to_json(image_path):
    """
    Распознает текст на изображении, сохраняет координаты и текст в JSON файл.

    Args:
        image_path (str): Путь к изображению.
    """
    try:
        # Проверка, существует ли файл
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found at '{image_path}'")

        # Настройка пути к tesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        # Распознавание текста с указанием языков
        image = Image.open(image_path)
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

        # Определение имени JSON файла
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        json_file_name = f'{base_name}.json'

        # Получение пути к папке, где находится скрипт
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Формирование полного пути к JSON файлу
        json_file_path = os.path.join(script_dir, json_file_name)

        # Запись JSON данных в файл
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        return json_file_path  # Возвращаем путь к созданному JSON файлу

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during OCR: {e}")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ocr")
async def process_image(request: Request, image_path: str = Form(...)):
    """
    Получает путь к изображению, выполняет OCR и возвращает JSON файл на скачивание.
    """
    try:
        json_file_path = ocr_image_to_json(image_path)  # Вызываем функцию OCR

        # Возвращаем файл на скачивание
        return FileResponse(
            path=json_file_path,
            filename=os.path.basename(json_file_path),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(json_file_path)}"},
        )

    except HTTPException as e:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": e.detail}, status_code=e.status_code)

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": f"An unexpected error occurred: {e}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)