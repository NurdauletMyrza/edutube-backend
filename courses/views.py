from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView

from .models import Course, Module, Lesson
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, CourseDetailSerializer, LessonDetailSerializer
from rest_framework.permissions import AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
# from oauth2client.service_account import ServiceAccountCredentials
import io


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


# class GoogleDriveUploadURLView(APIView):
#     def post(self, request):
#         file_name = request.data.get("filename")
#         mime_type = request.data.get("mime_type", "application/octet-stream")
#
#         # аутентификация
#         credentials = ServiceAccountCredentials.from_json_keyfile_name(
#             'credentials.json',
#             scopes=['https://www.googleapis.com/auth/drive']
#         )
#         service = build('drive', 'v3', credentials=credentials)
#
#         # создаём файл в Google Drive
#         file_metadata = {'name': file_name}
#         media = MediaIoBaseUpload(io.BytesIO(b""), mimetype=mime_type)
#         file = service.files().create(body=file_metadata, media_body=media).execute()
#
#         return Response({
#             'fileId': file.get('id'),
#             'webViewLink': f"https://drive.google.com/file/d/{file.get('id')}/view"
#         })
#
#
# class SaveDriveFileView(CreateAPIView):
#     queryset = LessonFile.objects.all()
#     serializer_class = LessonFileSerializer
#
#
# class DriveFileInfoView(APIView):
#     def get(self, request, file_id):
#         credentials = ServiceAccountCredentials.from_json_keyfile_name(
#             'credentials.json',
#             scopes=['https://www.googleapis.com/auth/drive']
#         )
#         service = build('drive', 'v3', credentials=credentials)
#         file = service.files().get(fileId=file_id, fields='id, name, mimeType, webViewLink, webContentLink').execute()
#
#         return Response({
#             'id': file['id'],
#             'name': file['name'],
#             'mimeType': file['mimeType'],
#             'webViewLink': file['webViewLink'],
#             'webContentLink': file.get('webContentLink')
#         })
