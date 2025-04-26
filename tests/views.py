from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from courses.models import Lesson
from .models import Test
# Импортируй Celery таск если будет использоваться

class GenerateTestView(APIView):
    def post(self, request):
        lesson_id = request.data.get("lessonId")
        if not lesson_id:
            return Response({"error": "lessonId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lesson = Lesson.objects.select_related("module__course").get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

        # Тут можешь запустить Celery таск с транскрибацией и генерацией теста
        # generate_test_task.delay(lesson.id)

        return Response({"message": "Тест генерируется, это может занять до 5 минут"}, status=status.HTTP_202_ACCEPTED)
