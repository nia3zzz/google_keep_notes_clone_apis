from django.db import models
from uuid import uuid4
from users.models import User
from django.utils import timezone


# Create your models here.
class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.user.email}"
