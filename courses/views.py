from rest_framework import generics
from .models import Course, Module, Lesson
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, CourseDetailSerializer
from rest_framework.permissions import AllowAny


class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        # Автоматически ставим текущего пользователя как автора
        serializer.save(author=self.request.user)


# class CourseDetailView(generics.RetrieveAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [AllowAny]
#     lookup_field = 'id'


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]



class AllCoursesView(generics.ListAPIView):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


class UserCreatedCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(author=self.request.user)


class ModuleCreateView(generics.CreateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class LessonCreateView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# # 🔹 Создание и просмотр всех курсов
# class CourseListCreateView(generics.ListCreateAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
#
# # 🔹 Получить, обновить или удалить конкретный курс
# class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
