# from fastapi import FastAPI
# from app.routers import auth

# app = FastAPI()

# app.include_router(auth.router)

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the FastAPI app!"}

# main.py
import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
import os


from .auth.auth_handler import get_current_user

from .routers import auth
from .routers import user
from .routers import indices

from .database import init_tables

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


class RequiresLoginException(Exception):
    pass

# redirection block
@app.exception_handler(RequiresLoginException)
async def exception_handler(request: Request, exc: RequiresLoginException) -> Response:
    ''' this handler allows me to route the login exception to the login page.'''
    return RedirectResponse(url='/') 

@app.middleware("http")
async def create_auth_header(
    request: Request,
    call_next,):
    '''
    Check if there are cookies set for authorization. If so, construct the
    Authorization header and modify the request (unless the header already
    exists!)
    '''
    if ("Authorization" not in request.headers 
        and "Authorization" in request.cookies
        ):
        access_token = request.cookies["Authorization"]
        
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer {access_token}".encode(),
            )
        )
    elif ("Authorization" not in request.headers 
        and "Authorization" not in request.cookies
        ): 
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer 12345".encode(),
            )
        )
        
    
    response = await call_next(request)
    return response    


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print(app_root)
    return templates.TemplateResponse("index.html",
     {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def signup(request: Request):
    print(app_root)
    return templates.TemplateResponse("register.html",
     {"request": request})

# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     print(app_root)

    
#     # print(current_user)
#     # if current_user is None:
#     #     return RedirectResponse(url='/')
#     try:
#         current_user = await get_current_user()
#         print("test", request)
#         return templates.TemplateResponse("dashboard.html",
#         {"request": request})
#     except Exception as e:
#         print(e)
#         raise RequiresLoginException()

# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request, ):
#     # print(access_token)
#     # current_user = await get_current_user(access_token=access_token)
#     # print(current_user)
#     if access_token is None:
#         # Redirect to login if no token is found in cookies
#         return RedirectResponse(url="/")

#     try:
#         # Validate the token and fetch the user
#         current_user = await get_current_user(access_token=access_token)
#         print(current_user)
#         return templates.TemplateResponse(
#             "dashboard.html",
#             {"request": request, "user": current_user}
#         )
#     except HTTPException as e:
#         # Redirect to login on token validation failure
#         print(e)
#         return RedirectResponse(url="/")
    
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, current_user: str = Depends(get_current_user)
):
    # print("gcu",get_current_user())
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})

@app.get("/dashboard_test", response_class=HTMLResponse)
async def dashboard_test(
    request: Request, current_user: str = Depends(get_current_user)
):
    # print("gcu",get_current_user())
    return templates.TemplateResponse("dashboard_test.html", {"request": request, "user": current_user})

app.include_router(user.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(indices.router)

if __name__ == "__main__":
    init_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)