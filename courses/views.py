from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from utils.google_drive_service import get_drive_service

from .models import Course, Module, Lesson, LessonFile, Enrollment
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, CourseDetailSerializer, LessonDetailSerializer, LessonFileSerializer

from google.auth.transport.requests import AuthorizedSession
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import HttpRequest
from googleapiclient.errors import HttpError

import os

class IsEnrolledInCourse(APIView):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        return Response({'is_enrolled': is_enrolled})


class EnrolledCourses(APIView):
    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        courses = [enrollment.course for enrollment in enrollments]
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class EnrollInCourse(APIView):
    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
            if created:
                return Response({"success": "Successfully enrolled"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Already enrolled"}, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)


class CourseCreateView(CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# class CourseDetailView(generics.RetrieveAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [AllowAny]
#     lookup_field = 'id'


class CourseDetailView(RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]


class AllCoursesView(ListAPIView):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


class UserCreatedCoursesView(ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(author=self.request.user)


class ModuleCreateView(CreateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class LessonCreateView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDetailView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    lookup_field = 'id'
    # permission_classes = [AllowAny]


class GetUploadURLView(APIView):
    def post(self, request):
        filename = request.data.get("filename")
        mime_type = request.data.get("mime_type", "application/octet-stream")

        service, credentials = get_drive_service()
        authed_session = AuthorizedSession(credentials)

        # Шаг 1: создаем файл (получаем fileId)
        file_metadata = {
            "name": filename,
            "parents": [os.getenv('DRIVE_FOLDER_ID')],
            "mimeType": mime_type,
        }

        metadata_response = service.files().create(
            body=file_metadata,
            fields="id"
        ).execute()

        file_id = metadata_response.get("id")

        upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=resumable"

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": mime_type,
        }

        # ⚠️ не включаем "parents" в тело запроса
        session_response = authed_session.patch(
            upload_url,
            headers=headers,
            json={"name": filename, "mimeType": mime_type}
        )

        # file_id = metadata_response.get("id")
        #
        # # Шаг 2: получаем upload_url для этого fileId
        # upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=resumable"
        #
        # headers = {
        #     "Content-Type": "application/json; charset=UTF-8",
        #     "X-Upload-Content-Type": mime_type,
        # }
        #
        # session_response = authed_session.patch(
        #     upload_url,
        #     headers=headers,
        #     json=file_metadata
        # )

        if session_response.status_code in [200, 201]:
            return Response({
                "fileId": file_id,
                "upload_url": session_response.headers.get("Location")
            })
        else:
            return Response({
                "error": "Failed to create upload session",
                "status_code": session_response.status_code,
                "details": session_response.text
            }, status=500)


class SaveLessonFileView(APIView):
    def post(self, request):
        file_id = request.data.get("file_id")

        # 1. Получаем информацию о файле с Google Drive
        try:
            service, credentials = get_drive_service()
            file_info = service.files().get(fileId=file_id, fields="id, name, size").execute()
        except HttpError as e:
            return Response(
                {"error": "File not found", "details": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Проверяем размер файла
        file_size = int(file_info.get("size", 0))
        if file_size == 0:
            return Response(
                {"error": "File exist, but content empty (size 0 bites)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Сохраняем файл в базе данных
        serializer = LessonFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "File saved", "file": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonFilesListView(APIView):
    def get(self, request, lesson_id):
        files = LessonFile.objects.filter(lesson_id=lesson_id)
        serializer = LessonFileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteLessonFileView(APIView):
    def delete(self, request, pk):
        try:
            lesson_file = LessonFile.objects.get(pk=pk)
        except LessonFile.DoesNotExist:
            return Response({"detail": "File not found in database"}, status=status.HTTP_404_NOT_FOUND)

        file_id = lesson_file.file_id

        # Удаляем из Google Drive
        try:
            service, _ = get_drive_service()
            service.files().delete(fileId=file_id).execute()
        except HttpError as e:
            if e.resp.status == 404:
                # Файл уже удален — не критично
                pass
            else:
                return Response({"detail": f"Error Drive storage file delete action: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Удаляем из базы
        lesson_file.delete()

        return Response({"success": "File successfully removed from storage"}, status=status.HTTP_200_OK)
