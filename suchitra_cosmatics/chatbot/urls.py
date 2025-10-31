from django.urls import path
from .views import ChatbotView

urlpatterns = [
    path('api/chatbot/', ChatbotView.as_view(), name='chatbot_api'),
]