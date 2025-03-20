from rest_framework import serializers
from .models import Course, Enrollment, Topic, CourseFile

class CourseFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFile
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    files = CourseFileSerializer(many=True, required=False)

    class Meta:
        model = Topic
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    files = CourseFileSerializer(many=True, read_only=True)
    student_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def create(self, validated_data):
        # Автоматически добавляем teacher, если его нет
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
