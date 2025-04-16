from django.urls import path
from .views import CourseCreateView, CourseDetailView, AllCoursesView, UserCreatedCoursesView

urlpatterns = [
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('all/', AllCoursesView.as_view(), name='all-courses'),
    path('user-created/', UserCreatedCoursesView.as_view(), name='user-created'),

    # path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    # path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
]
