import uvicorn

from fastapi import FastAPI

from src.routes import users, tags, comments, images

app = FastAPI()

app.include_router(users.router, prefix='/api')
app.include_router(tags.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(images.router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello Team"}


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
