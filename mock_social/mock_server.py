from __future__ import annotations

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="Guardrailed X Agent Harness API", version="0.1.0")
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# In-memory posted store for tests
posted_texts: list[str] = []

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    import traceback
    return HTMLResponse(content=f"<h1>Internal Server Error</h1><pre>{traceback.format_exc()}</pre>", status_code=500)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    # Simple auth - accept any
    # In real test, could validate
    return RedirectResponse(url="/compose/tweet", status_code=303)

@app.get("/compose/tweet", response_class=HTMLResponse)
def compose_page(request: Request):
    last_posted = posted_texts[-1] if posted_texts else ""
    return templates.TemplateResponse(
        request=request,
        name="compose.html",
        context={"last_posted": last_posted, "tweets": list(reversed(posted_texts))},
    )

@app.post("/api/tweet")
def post_tweet(text: str = Form(...)):
    posted_texts.append(text)
    return {"status": "ok", "text": text}

@app.get("/api/tweets")
def get_all_tweets():
    return {"count": len(posted_texts), "tweets": posted_texts}

@app.post("/api/internal/reset")
def reset():
    posted_texts.clear()
    return {"status": "reset"}

# For Playwright to verify success, we serve compose page with success indicator after POST via JS?
# We'll handle via HTML form action to /api/tweet and then redirect back with query param.
# Simpler: compose.html contains JS that intercepts post and shows success.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
