# from fastapi import FastAPI
# from app.routers import auth

# app = FastAPI()

# app.include_router(auth.router)

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the FastAPI app!"}

# main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
import os

from .routers import auth
from .routers import user

app = FastAPI(debug=True)

origins = [
    "http://localhost:5174",
    # Add more origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

# load templates
# env = jinja2.Environment(loader=PackageLoader("./../../ui"))
app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
templates = Jinja2Templates(directory=f"{app_root}/ui")
# templates = env.get_template()
# templates = Jinja2Templates(directory=Path(__file__).parent.parent+ "ui/")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print(app_root)
    return templates.TemplateResponse("index.html",
     {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def index(request: Request):
    print(app_root)
    return templates.TemplateResponse("register.html",
     {"request": request})

app.include_router(user.router)
app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)