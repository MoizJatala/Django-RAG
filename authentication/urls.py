from django.urls import path
from .views import UserSignupView, UserLoginView, UploadDocumentView, QueryDocumentView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('document/', UploadDocumentView.as_view(), name='fastapi-upload'),
    path('query/', QueryDocumentView.as_view(), name='fastapi-query'),
    # Other authentication URLs
]
