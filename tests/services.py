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
    def update_status(text):
        test.status = text
        test.save(update_fields=["status"])

    try:
        update_status("Collecting lesson data...")
        lesson_title = lesson.title
        lesson_content = lesson.content
        module = lesson.module
        course = module.course

        update_status("Searching lesson video...")
        lesson_files = LessonFile.objects.filter(lesson=lesson)
        if not lesson_files.exists():
            test.is_generating = False
            update_status("Lesson file does not exist...")
            test.save(update_fields=["is_generating"])
            return

        file_id = lesson_files.first().file_id
        update_status("Downloading lesson video file...")
        video_path = download_file_from_drive(file_id)
        update_status("Extracting audio from video...")
        audio_path = extract_audio(video_path)
        update_status("Audio transcription...")
        transcription = transcribe_with_vosk(audio_path)

        os.remove(video_path)
        os.remove(audio_path)

        update_status("Generating test with AI...")
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

        update_status("Storing questions in database...")
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
        update_status("AI test is ready")
        test.save(update_fields=["is_generating", "status"])

    except Exception as e:
        test.is_generating = False
        update_status(f"Error: {str(e)}")
        test.save(update_fields=["is_generating", "status"])
        print(f"[ERROR while generating test #{test.id}] {e}")
