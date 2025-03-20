from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, EnrollmentViewSet, TopicViewSet, CourseFileViewSet, UploadFileView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'files', CourseFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
urlpatterns += [
    path('upload-file/', UploadFileView.as_view(), name='upload_file'),
]