from django.db import models
from uuid import uuid4
from django.utils import timezone


# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    profile_picture_url = models.CharField(
        max_length=300,
        default="https://images.ctfassets.net/h6goo9gw1hh6/2sNZtFAWOdP1lmQ33VwRN3/24e953b920a9cd0ff2e1d587742a2472/1-intro-photo-final.jpg?w=1200&h=992&fl=progressive&q=70&fm=jpg",
    )
    password = models.CharField(max_length=300)
    created_at = models.DateTimeField(default=timezone.now(), editable=False)
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.email
