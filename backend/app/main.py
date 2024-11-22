# from fastapi import FastAPI
# from app.routers import auth

# app = FastAPI()

# app.include_router(auth.router)

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the FastAPI app!"}

# main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(user.router)
app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)