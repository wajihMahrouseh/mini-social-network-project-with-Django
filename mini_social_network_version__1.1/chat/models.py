from django.db import models

from users.models import Profile


class Message(models.Model) :
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at',]

    def __str__(self):
        return self.text
