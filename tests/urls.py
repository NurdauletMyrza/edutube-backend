from django.urls import path
from .views import GenerateTestForLesson, TestByLessonAPIView

urlpatterns = [
    path('test/generate/', GenerateTestForLesson.as_view(), name='test_generate'),
    path('test/lesson/<int:lesson_id>/', TestByLessonAPIView.as_view(), name='test-detail'),
]