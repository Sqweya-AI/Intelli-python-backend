from django.db import models

# Create your models here.

class Post(models.Model):
    title       = models.TextField(blank=True)
    description = models.TextField(blank=True)
    imageUrl    = models.URLField(blank=True)
    category    = models.CharField(max_length=200, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
    