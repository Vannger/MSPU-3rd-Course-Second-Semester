from fastapi import FastAPI,Request,Form,HTTPException,Depends,Header,status
from src.schemes import UserCreate
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
import bleach

app = FastAPI()
templates = Jinja2Templates(directory="templates")
users_db = {
    "alice": {"username": "alice", "role": "user"},
    "bob": {"username": "bob", "role": "user"},
    "admin": {"username": "admin", "role": "admin"},
}
files_db = [
    {"id": 1, "filename": "report_alice.pdf", "owner": "alice", "size": 1024},
    {"id": 2, "filename": "photo_bob.jpg", "owner": "bob", "size": 2048},
    {"id": 3, "filename": "admin_keys.txt", "owner": "admin", "size": 12},
]

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in ["/docs"]:
        return response
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:;"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    return response

def clean_html(text: str) -> str:
    allowed_tags = ['b', 'i', 'u', 'em', 'strong']
    return bleach.clean(text, tags=allowed_tags, attributes={}, strip=True)

@app.post("/registration")
def register_user(user: UserCreate) -> dict:
    return {"msg": "User created", "user": user.username}

comments_db = []

@app.get("/comments" ,response_class=HTMLResponse)
async def get_comments(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="comments.html", 
    context={"request": request, "comments": comments_db}
)


@app.post("/comments" ,response_class=HTMLResponse)
async def post_comment(request: Request, user_comment: str = Form(...)):
    safe_message = clean_html(user_comment)
    comments_db.append(safe_message)
    return templates.TemplateResponse(
    request=request, 
    name="comments.html", 
    context={"request": request, "comments": comments_db}
)

async def get_current_user(x_user: str = Header(..., description="Имя пользователя для авторизации")) -> dict:
    if x_user not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or missing auth header"
        )
    return users_db[x_user]

async def checkfile_permissions(file_id: int, current_user: dict = Depends(get_current_user)) -> dict:
    file = next((f for f in files_db if f["id"] == file_id), None)
    
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    is_owner = file["owner"] == current_user["username"]
    is_admin = current_user["role"] == "admin"
    
    if not (is_owner or is_admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
    return file

@app.get("/files/{file_id}", response_model=Dict[str, Any])
async def get_file_info(file: dict = Depends(checkfile_permissions)):
    return file

@app.delete("/files/{file_id}")
async def delete_file(file: dict = Depends(checkfile_permissions)):
    global files_db

    files_db = [f for f in files_db if f["id"] != file["id"]]
    return {"message": f"File '{file['filename']}' successfully deleted"}


@app.get("/files/my")
async def get_my_files(current_user: dict = Depends(get_current_user)):
    user_files = [f for f in files_db if f["owner"] == current_user["username"]]
    return user_files


@app.get("/files/all")
async def get_all_files(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only administrators have access to this resource"
        )
    return files_db
