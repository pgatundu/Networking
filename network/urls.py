
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newPost", views.newPost, name="newPost"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
     path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('like-status/<int:post_id>/', views.get_like_status, name='get_like_status'),
]
