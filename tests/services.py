import os
import json

from courses.models import LessonFile
from .models import Question, Option
from .utils import (
    call_openai_api,
    download_file_from_drive,
    extract_audio,
    transcribe_with_vosk
)

questions_number = 5

def generate_test_content(lesson, test):
    try:
        lesson_title = lesson.title
        lesson_content = lesson.content
        module = lesson.module
        course = module.course

        lesson_files = LessonFile.objects.filter(lesson=lesson)
        if not lesson_files.exists():
            test.is_generating = False
            test.save(update_fields=["is_generating"])
            return

        file_id = lesson_files.first().file_id
        video_path = download_file_from_drive(file_id)
        audio_path = extract_audio(video_path)
        transcription = transcribe_with_vosk(audio_path)

        os.remove(video_path)
        os.remove(audio_path)

        system_message = (
            "You are an experienced teacher. Based on the provided educational material, "
            f"generate {questions_number} multiple-choice quiz questions in JSON format. "
            "Each question must have 4 answer options, where the first option is always correct. "
            f"Return only a valid JSON array of {questions_number} objects. Each object must contain: "
            "'question' (string), 'options' (a list of 4 strings), and 'correct_answer' (always 'A')."
        )
        user_message = (
            f"Course: {course.title}\n"
            f"Course Description: {course.description}\n\n"
            f"Module: {module.title}\n"
            f"Module Description: {module.description}\n\n"
            f"Lesson: {lesson_title}\n"
            f"Lesson Content: {lesson_content}\n\n"
            f"Lesson Transcription: {transcription}\n\n"
            f"Create {questions_number} multiple-choice questions based on the transcription. "
            f"Return only a valid JSON array in this format:\n"
            f'[\n'
            f'  {{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "A"}},\n'
            f'  ... (total {questions_number} such objects) ...\n'
            f']'
        )

        test_json = json.loads(call_openai_api(system_message, user_message))

        for q in test_json:
            question_text = q.get("question")
            options = q.get("options", [])
            correct_index = 0  # 'A' — это первый вариант

            if not question_text or len(options) != 4:
                continue
            question = Question.objects.create(test=test, text=question_text)
            for i, option_text in enumerate(options):
                Option.objects.create(
                    question=question,
                    text=option_text,
                    is_correct=(i == correct_index)
                )

        test.is_generating = False
        test.save(update_fields=["is_generating"])

    except Exception as e:
        test.is_generating = False
        test.save(update_fields=["is_generating"])
        print(f"[ERROR while generating test #{test.id}] {e}")
