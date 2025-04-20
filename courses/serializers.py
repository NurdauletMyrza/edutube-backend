from rest_framework import serializers
from .models import Course, Module, Lesson

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['author', 'created_at']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'
        read_only_fields = ['created_at']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['created_at']


class ModuleWithLessonsSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'created_at', 'lessons']


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleWithLessonsSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'author', 'created_at', 'modules']





class CourseShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'author']


class ModuleShortSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'course']


class LessonDetailSerializer(serializers.ModelSerializer):
    module = ModuleShortSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order', 'created_at', 'module']


# class LessonFileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LessonFile
#         fields = '__all__'