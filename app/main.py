from fastapi import FastAPI
from app.routes import user


def create_application():
    application = FastAPI(debug=True)
    application.include_router(user.user_router)
    return application


app = create_application()


@app.get("/")
async def root():
    return {"message": "Hi, I am Describly. Awesome - Your setrup is done & working."}