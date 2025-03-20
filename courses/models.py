from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_courses")
    title = models.CharField(max_length=255)
    description = models.TextField()
    students = models.ManyToManyField(User, related_name="enrolled_courses", through='Enrollment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CourseFile(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="files", null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="files", null=True, blank=True)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.course.title if self.course else self.topic.title}"
