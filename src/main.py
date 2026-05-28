from fastapi import FastAPI,Request,Form
from src.schemes import UserCreate
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import bleach

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
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
