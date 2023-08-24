from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import solara.server.fastapi

app = FastAPI()


@app.get("/")
def read_root():
    return RedirectResponse(url="/app/")


app.mount("/app/", app=solara.server.fastapi.app)