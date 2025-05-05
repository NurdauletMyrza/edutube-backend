import os
import json
import tempfile
import requests
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from dotenv import load_dotenv
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from courses.models import Lesson, LessonFile
from .models import Test, Question, Option
from .serializers import TestSerializer
from .utils import (
    call_openai_api,
    download_file_from_drive,
    extract_audio,
    transcribe_with_vosk
)

questions_number = 5
load_dotenv()

class GenerateTestForLesson(APIView):
    def post(self, request, *args, **kwargs):
        try:
            lesson_id = request.POST.get('lessonId')
            if not lesson_id:
                return JsonResponse({"error": "lessonId is required"}, status=400)

            lesson = Lesson.objects.select_related('module__course').get(id=lesson_id)
            lesson_title = lesson.title
            lesson_content = lesson.content
            module_title = lesson.module.title
            module_description = lesson.module.description
            course_title = lesson.module.course.title
            course_description = lesson.module.course.description

            lesson_files = LessonFile.objects.filter(lesson=lesson)
            if not lesson_files.exists():
                return JsonResponse({"error": "No video files found for this lesson"}, status=404)

            file_id = lesson_files.first().file_id
            video_path = download_file_from_drive(file_id)
            audio_path = extract_audio(video_path)
            transcription = transcribe_with_vosk(audio_path)

            # test = Test.objects.create(lesson=lesson)
            #
            # for i in range(5):
            #     system_message = (
            #         "You are an experienced teacher. Create quiz questions with multiple-choice answers "
            #         "based on the provided educational material. The first answer option should always be correct."
            #     )
            #
            #     user_message = (
            #         f"Course: {course_title}\n"
            #         f"Course Description: {course_description}\n\n"
            #         f"Module: {module_title}\n"
            #         f"Module Description: {module_description}\n\n"
            #         f"Lesson: {lesson_title}\n"
            #         f"Lesson Content: {lesson_content}\n\n"
            #         f"Lesson Transcription: {transcription}\n\n"
            #         f"Create one multiple-choice question based on the transcription. Provide 4 answer options, "
            #         f"where the first one is always correct."
            #     )
            #     question_text = call_openai_api(system_message, user_message)
            #
            #     question_lines = question_text.split("\n")
            #     question_title = question_lines[0]
            #     options = question_lines[1:]
            #
            #     question = Question.objects.create(test=test, text=question_title)
            #
            #     for idx, option_text in enumerate(options):
            #         is_correct = idx == 0
            #         Option.objects.create(question=question, text=option_text.strip(), is_correct=is_correct)

            os.remove(video_path)
            os.remove(audio_path)

            system_message = (
                "You are an experienced teacher. Based on the provided educational material, "
                "generate 5 multiple-choice quiz questions in JSON format. "
                "Each question must have 4 answer options, where the first option is always correct. "
                "Return only a valid JSON array of 5 objects. Each object must contain: "
                "'question' (string), 'options' (a list of 4 strings), and 'correct_answer' (always 'A')."
            )
            user_message = (
                f"Course: {course_title}\n"
                f"Course Description: {course_description}\n\n"
                f"Module: {module_title}\n"
                f"Module Description: {module_description}\n\n"
                f"Lesson: {lesson_title}\n"
                f"Lesson Content: {lesson_content}\n\n"
                f"Lesson Transcription: {transcription}\n\n"
                f"Create 5 multiple-choice questions based on the transcription. "
                f"Return only a valid JSON array in this format:\n"
                f'[\n'
                f'  {{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "A"}},\n'
                f'  ... (total 5 such objects) ...\n'
                f']'
            )

            test_json = json.loads(call_openai_api(system_message, user_message))

            for question in test_json:
                print(question['question'])
                for option in question['options']:
                    print(option)
                print(question['correct_answer'])
                print('-----------------------')

            return JsonResponse({
                "lesson_title": lesson_title,
                # "test_id": test.id,
                "test_id": 2,
                "message": "Test generated and saved successfully."
            })

        except Lesson.DoesNotExist:
            return JsonResponse({"error": "Lesson not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class TestDetailAPIView(APIView):
    def get(self, request, test_id):
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestSerializer(test)
        return Response(serializer.data)