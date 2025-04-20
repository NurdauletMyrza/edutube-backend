from django.urls import path
from .views import CourseCreateView, CourseDetailView, AllCoursesView, UserCreatedCoursesView, ModuleCreateView, \
    LessonCreateView, LessonDetailView

urlpatterns = [
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('all/', AllCoursesView.as_view(), name='all-courses'),
    path('user-created/', UserCreatedCoursesView.as_view(), name='user-created'),
    path('module/create/', ModuleCreateView.as_view(), name='module-create'),
    path('lesson/create/', LessonCreateView.as_view(), name='lesson-create'),
    path('lesson/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),

    # path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    # path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
]
