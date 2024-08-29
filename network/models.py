from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib import admin



class User(AbstractUser):
    pass



class Post(models.Model):
    content = models.CharField(max_length=260)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Posted {self.id} by {self.user} on {self.date.strftime('%I:%M %p %b %d %Y')}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_following")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_being_followed")

    def __str__(self):
        return f"{self.user} is following {self.user_follower}" 
    
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('post', 'user')  # Ensures a user can only like/unlike a post once

    def __str__(self):
        return f"{self.user.username} - {self.post.id} - {'Liked' if self.liked else 'Unliked'}"