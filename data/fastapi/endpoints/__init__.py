from .user import router as user_router
from .posts import router as posts_router

routers = [
    user_router,
    posts_router,
]
