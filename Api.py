from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# templates/index.html:
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Subtraction Calculator</title>
# </head>
# <body>
#     <h1>Subtraction Calculator</h1>
#     <form action="/subtract" method="post">
#         <label for="num1">Number 1:</label>
#         <input type="number" id="num1" name="num1" required><br><br>

#         <label for="num2">Number 2:</label>
#         <input type="number" id="num2" name="num2" required><br><br>

#         <button type="submit">Subtract</button>
#     </form>

#     {% if result %}
#         <h2>Result: {{ result }}</h2>
#     {% endif %}
# </body>
# </html>

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})


@app.post("/subtract", response_class=HTMLResponse)
async def subtract(request: Request, num1: float = Form(...), num2: float = Form(...)):
    try:
        result = num1 - num2
        return templates.TemplateResponse("index.html", {"request": request, "result": result})
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input: Please enter numbers only.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)