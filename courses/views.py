import os

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Course, Enrollment, Topic, CourseFile
from .serializers import CourseSerializer, EnrollmentSerializer, TopicSerializer, CourseFileSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .services.google_drive import upload_to_drive

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print("Performing create...")
        print(f"Current user: {self.request.user}")
        serializer.save(teacher=self.request.user)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        user = request.user
        if Enrollment.objects.filter(user=user, course_id=course_id).exists():
            return Response({'message': 'Вы уже записаны на этот курс'}, status=400)
        return super().create(request, *args, **kwargs)

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseFileViewSet(viewsets.ModelViewSet):
    queryset = CourseFile.objects.all()
    serializer_class = CourseFileSerializer
    permission_classes = [permissions.IsAuthenticated]

class UploadFileView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES['file']
        topic_id = request.data.get('topic_id')

        file_path = f'temp/{file_obj.name}'
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        file_url = upload_to_drive(file_path, file_obj.name)
        os.remove(file_path)

        course_file = CourseFile.objects.create(topic_id=topic_id, file_url=file_url)

        return Response({"file_url": file_url, "file_id": course_file.id})
