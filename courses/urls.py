from django.urls import path
from .views import CourseCreateView, CourseDetailView, AllCoursesView, UserCreatedCoursesView, ModuleCreateView, \
    LessonCreateView, LessonDetailView, GetUploadURLView, SaveLessonFileView, DeleteLessonFileView, LessonFilesListView, \
    EnrollInCourse, EnrolledCourses, IsEnrolledInCourse

urlpatterns = [
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('all/', AllCoursesView.as_view(), name='all-courses'),
    path('user-created/', UserCreatedCoursesView.as_view(), name='user-created'),
    path('module/create/', ModuleCreateView.as_view(), name='module-create'),
    path('lesson/create/', LessonCreateView.as_view(), name='lesson-create'),
    path('lesson/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),

    path("file/upload-url/", GetUploadURLView.as_view(), name="get-upload-url"),
    path("file/save-file/", SaveLessonFileView.as_view(), name="save-lesson-file"),
    path("files/get-lesson-files/<int:lesson_id>/", LessonFilesListView.as_view(), name="get-lesson-files"),
    path("file/delete-lesson-file/<int:pk>/", DeleteLessonFileView.as_view(), name="delete-lesson-file"),

    path('course/enroll/<int:course_id>/', EnrollInCourse.as_view(), name='enroll-in-course'),
    path('user-enrolled/', EnrolledCourses.as_view(), name='enrolled-courses'),
    path('is-enrolled-course/<int:course_id>/', IsEnrolledInCourse.as_view(), name='is-enrolled-course'),

    # path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    # path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
]
