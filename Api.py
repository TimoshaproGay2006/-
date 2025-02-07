from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

import os
import shutil
import tempfile  # Corrected import
from tempfile import SpooledTemporaryFile # Corrected import

app = FastAPI()
templates = Jinja2Templates(directory="templates")

async def copy_to_tempfile(file_path: str) -> SpooledTemporaryFile:
    """Copies the content of the file to a temporary file."""
    try:
        # Open the original file in binary read mode
        with open(file_path, "rb") as source_file:
            # Create a temporary file using SpooledTemporaryFile (in-memory if small, disk if large)
            temp_file = SpooledTemporaryFile(max_size=10 * 1024 * 1024) # 10MB max in-memory
            # Copy the content
            shutil.copyfileobj(source_file, temp_file)
            temp_file.seek(0) # Reset the file pointer to the beginning
            return temp_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error copying file: {e}")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/rename")
async def rename_file(request: Request, file_path: str = Form(...)):
    """Renames a file and returns it as a download."""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="File not found")

        file_extension = os.path.splitext(file_path)[1]
        temp_file_name = f"111{file_extension}"

        # Copy file to temporary file
        temp_file = await copy_to_tempfile(file_path)

        # Create a streaming response that reads from the temp file
        async def generate():
            while True:
                chunk = temp_file.read(8192) # 8KB chunks
                if not chunk:
                    break
                yield chunk

        # Return the streaming response
        return StreamingResponse(
            generate(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment;filename={temp_file_name}"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'temp_file' in locals():
            temp_file.close()  # Close the temp file, which will delete it

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)