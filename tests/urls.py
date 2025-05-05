from django.urls import path
from .views import GenerateTestForLesson, TestDetailAPIView

urlpatterns = [
    path('test/generate/', GenerateTestForLesson.as_view(), name='test_generate'),
    path('test/<int:test_id>/', TestDetailAPIView.as_view(), name='test-detail'),
]