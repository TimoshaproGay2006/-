from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
import os
import shutil

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/copy")
async def copy_file(request: Request, file_path: str = Form(...)):
    """
    Копирует файл и отдает его на скачивание.
    """
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="File not found")

        # Получаем расширение файла
        file_extension = os.path.splitext(file_path)[1]

        # Создаем новое имя файла
        new_file_name = f"12345{file_extension}"
        new_file_path = os.path.join(".", new_file_name)  # Создаем в текущей директории для простоты

        # Копируем файл с новым именем
        try:
            shutil.copy2(file_path, new_file_path)  # copy2 сохраняет метаданные (время и т.п.)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error copying file: {e}")


        # Возвращаем файл на скачивание
        return FileResponse(
            path=new_file_path,
            filename=new_file_name,
            media_type="application/octet-stream",  # Универсальный тип для скачивания
            headers={"Content-Disposition": f"attachment; filename={new_file_name}"},  # Указываем имя файла для скачивания
        )

    except HTTPException as e:
         return templates.TemplateResponse("index.html", {"request": request, "error_message": e.detail}, status_code=e.status_code)

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": f"An unexpected error occurred: {e}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)