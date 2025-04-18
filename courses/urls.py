from django.urls import path
from .views import CourseCreateView, CourseDetailView, AllCoursesView, UserCreatedCoursesView, ModuleCreateView, LessonCreateView

urlpatterns = [
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('all/', AllCoursesView.as_view(), name='all-courses'),
    path('user-created/', UserCreatedCoursesView.as_view(), name='user-created'),
    path('module/create/', ModuleCreateView.as_view(), name='module-create'),
    path('lesson/create/', LessonCreateView.as_view(), name='lesson-create'),

    # path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    # path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
]
