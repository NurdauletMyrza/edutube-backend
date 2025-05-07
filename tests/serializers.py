from rest_framework import serializers
from .models import Test, Question, Option
import random


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Проверяем, передан ли context с request
        request = self.context.get('request')
        if request:
            user = request.user
            # Идем через цепочку: Option → Question → Test → Lesson → Module → Course → author
            if instance.question.test.lesson.module.course.author != user:
                rep.pop('is_correct')  # Убираем правильный ответ
        return rep


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

    def get_options(self, obj):
        options = list(obj.options.all())
        random.shuffle(options)
        request = self.context.get('request')
        return OptionSerializer(options, many=True, context={'request': request}).data


class TestSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['id', 'lesson', 'created_at', 'is_generating', 'questions']

    def get_questions(self, obj):
        questions = list(obj.questions.all())
        random.shuffle(questions)
        request = self.context.get('request')
        return QuestionSerializer(questions, many=True, context={'request': request}).data
