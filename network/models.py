from django.contrib.auth.models import AbstractUser
from django.db import models




class User(AbstractUser):
    pass



class Post(models.Model):
    content = models.CharField(max_length=260)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    liked_users = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"Post {self.id} by {self.user} on {self.date.strftime('%I:%M %p %b %d %Y')}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_following")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_being_followed")

    def __str__(self):
        return f"{self.user} is following {self.user_follower}" 
    
class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name="post_like" )

    def __str__(self):
        return f"{self.user} liked {self.post}"