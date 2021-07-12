from django.db import models, transaction
from django.contrib.auth.models import User
from .base import Group, SourceVersion
from uuid import uuid4


class Page(models.Model):
    """A page for embedding content linked to a specific user"""

    name = models.TextField(null=False, blank=False)
    content = models.TextField(null=True, blank=True)
    users = models.ManyToManyField(User, related_name="pages", blank=True)
    needs_authentication = models.BooleanField(default=True)
    slug = models.SlugField(max_length=1000, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s " % (self.name,)
