from django.db import models
from uuid import uuid4
from users.models import User
from django.utils import timezone


# Create your models here.
class Notes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=300)
    note = models.TextField()
    files = models.JSONField(models.CharField(max_length=300), blank=True, default=list)
    collaborators = models.ManyToManyField(User, related_name="collaborations")
    created_at = models.DateTimeField(default=timezone.now(), editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
