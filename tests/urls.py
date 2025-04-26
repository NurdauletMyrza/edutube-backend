from django.urls import path
from .views import GenerateTestView
urlpatterns = [
    path('test/generate/', GenerateTestView.as_view(), name='test_generate'),
]
