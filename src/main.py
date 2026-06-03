from fastapi import FastAPI,Request,Form,HTTPException,Depends,Header,status,UploadFile, File, Query, Response
from src.schemes import UserCreate
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,FileResponse,JSONResponse
from typing import List, Dict, Any
from dotenv import load_dotenv
import bleach
import filetype
import uuid
import os
from cryptography.fernet import Fernet
from logger_config import logger


load_dotenv()

ENCRYPTION_KEY = os.getenv("APP_SECRET")
if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY is not set in .env file!")
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Критическая ошибка при запросе {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "We are sorry, something went wrong."}
    )



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

storage_dir = "storage"
os.makedirs(storage_dir, exist_ok=True)
MAX_FILE_SIZE = 2 * 1024 * 1024

@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...), 
    encrypt: bool = Query(False, description="Зашифровать файл перед сохранением"),
    current_user: dict = Depends(get_current_user)
):
    head = await file.read(2048) 
    kind = filetype.guess(head)
    if kind is None or kind.mime not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only real JPEG and PNG are allowed."
        )
    await file.seek(0)

    file_uuid = str(uuid.uuid4())
    save_path = os.path.join(storage_dir, file_uuid)
    total_size = 0
    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail="File is too large. Max allowed size is 2MB."
        )

    if encrypt:
        file_data = cipher_suite.encrypt(file_data)

    with open(save_path, "wb") as buffer:
        buffer.write(file_data)

    if encrypt:
        file_data = cipher_suite.encrypt(file_data)
    global files_db
    new_id = max([f.get("id", 0) for f in files_db], default=0) + 1
    new_record = {
        "id": new_id,
        "original_name": file.filename,
        "owner": current_user["username"],
        "size": total_size,
        "path": save_path,
        "is_encrypted": encrypt
    }
    files_db.append(new_record)
    return {"message": "File uploaded successfully", "file": new_record}

@app.get("/files/{file_id}/download")
async def download_file(file_record: dict = Depends(checkfile_permissions)):

    if "path" not in file_record or not os.path.exists(file_record["path"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Physical file not found on server"
        )

    with open(file_record["path"], "rb") as buffer:
        file_data=buffer.read()

    if file_record.get("is_encrypted"):
        try:
            file_data = cipher_suite.decrypt(file_data)
        except Exception:
            raise HTTPException(status_code=500, detail="Decryption failed. Invalid key or corrupted data.")
        
    return Response(
        content=file_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_record["original_name"]}"'}
    )

@app.get("/cause_error")
async def cause_error():
    logger.info("Пользователь вызвал тестовую ошибку /cause_error")
    return 1 / 0
@app.post("/login")
async def login_error(username:str = "user", password:str = "12345"):
    logger.warning("Пользователь вызвал ошибку логина")
    raise HTTPException(status_code=400, detail="Wrong password or login. Yall off the goop fr")