from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class UploadedFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    data = models.BinaryField()  # Stores file bytes directly
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} uploaded by {self.user}"
