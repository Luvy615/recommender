from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import user, product, wardrobe, search, chat
from backend.services.database import init_db

app = FastAPI(
    title="智能服装穿搭助手 API",
    description="基于AI的个人服装搭配助手后端服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(product.router)
app.include_router(wardrobe.router)
app.include_router(search.router)
app.include_router(chat.router)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "智能服装穿搭助手 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
