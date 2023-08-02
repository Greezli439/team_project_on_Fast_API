import uvicorn

from threading import Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.services.db_cleaner import clean_engine
from src.routes import users, tags, comments, images

app = FastAPI()


app.include_router(users.router, prefix='/api')
app.include_router(images.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(tags.router, prefix='/api')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello Team"}


thread = Thread(target=clean_engine)
thread.start()

if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
