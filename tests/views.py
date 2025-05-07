from threading import Thread

from django.http import JsonResponse
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from courses.models import Lesson, LessonFile
from .models import Test, Question, Option
from .serializers import TestSerializer
from .services import generate_test_content

load_dotenv()

class GenerateTestForLesson(APIView):
    def post(self, request, *args, **kwargs):
        try:
            lesson_id = request.data.get('lessonId')
            if not lesson_id:
                return JsonResponse({"error": "lessonId is required"}, status=400)

            lesson = Lesson.objects.select_related('module__course').get(id=lesson_id)

            # Удаляем старые тесты перед генерацией нового
            Test.objects.filter(lesson=lesson).delete()

            # Создаём Test с флагом генерации
            test = Test.objects.create(lesson=lesson, is_generating=True)

            # Запускаем генерацию в фоне
            generate_test_content(lesson, test)

            return JsonResponse({
                "test_id": test.id,
                "message": "Test already generated."
            })

        except Lesson.DoesNotExist:
            return JsonResponse({"error": "Lesson not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class LessonTestStatusView(APIView):
    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
            test = Test.objects.get(lesson=lesson)
            return JsonResponse({
                "test_id": test.id,
                "is_generating": test.is_generating,
                "status": test.status,
            })
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
        except Test.DoesNotExist:
            return JsonResponse({"error": "Test not found"}, status=404)


class TestDetailAPIView(APIView):
    def get(self, request, test_id):
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestSerializer(test)
        return Response(serializer.data)


class TestByLessonAPIView(APIView):
    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            test = Test.objects.get(lesson=lesson)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found for this lesson'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestSerializer(test)
        return Response(serializer.data)