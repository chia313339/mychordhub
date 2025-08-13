"""
API v1 main router.
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, songs, chords, collections, ratings
from app.api.api_v1.endpoints.music import transpose

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(songs.router, prefix="/songs", tags=["songs"])
api_router.include_router(chords.router, prefix="/chords", tags=["chords"])
api_router.include_router(collections.router, prefix="/collections", tags=["collections"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(transpose.router, prefix="/music", tags=["music"])