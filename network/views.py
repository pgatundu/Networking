from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django import template
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User,Post,Follow,Like


register = template.Library()


def add_like(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            if Like.objects.filter(user=request.user, post=post).exists():
                return JsonResponse({'error': 'You have already liked this post'}, status=400)
            Like.objects.create(user=request.user, post=post)
            post.like_count += 1
            post.save()         
            return JsonResponse({'like_count': post.like_count})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post does not exist'}, status=404)
        
def remove_like(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            like = Like.objects.filter(user=request.user, post=post).first()
            if not like:
                return JsonResponse({'error': 'You have not liked this post'}, status=400)
            
            # Delete the like entry
            like.delete()
            
            # Decrement the like count
            post.like_count -= 1
            post.save()
            return JsonResponse({'like_count': post.like_count})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post does not exist'}, status=404)


def edit(request,post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change Successful", "data": data["content"]})

def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if post.user != request.user:
            return JsonResponse({'error': 'You are not allowed to delete this post'}, status=403)
        
        post.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)



def index(request):
    allPosts = Post.objects.all().order_by("-id")
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    allLikes = Like.objects.all()
    whoYouLiked = []

    if request.user.is_authenticated:
        whoYouLiked = list(request.user.liked_posts.values_list('id', flat=True))
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)

    return render(request, "network/index.html", {
        "allPosts": allPosts,
        "posts_of_the_page": posts_of_the_page,
        "whoYouLiked": whoYouLiked
    })



def newPost(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allPosts = Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)

    # Check if the current user is following this profile
    try:
        checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(checkFollow) != 0:
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False

    # Determine which posts are liked by the current user
    liked_posts = Like.objects.filter(user=request.user).values_list('post', flat=True)
    liked_posts_set = set(liked_posts)  # For quick lookup

    # Paginator
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "allPosts": allPosts,
        "posts_of_the_page": posts_of_the_page,
        "username": user.username,
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing,
        "user_profile": user,
        "liked_posts_set": liked_posts_set  # Pass the liked posts set to the template
    })


def following(request):
    currentUser = request.user
    # Get users that the current user is following
    following_users = Follow.objects.filter(user_follower=currentUser).values_list('user', flat=True)
    
    # Fetch posts from users the current user is following
    following_posts = Post.objects.filter(user__in=following_users).order_by('-id')

    # Determine which posts are liked by the current user
    liked_posts = Like.objects.filter(user=currentUser).values_list('post', flat=True)
    liked_posts_set = set(liked_posts)  # For quick lookup

    # Paginator
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page,
        "liked_posts_set": liked_posts_set,
    })

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow(user=currentUser, user_follower=userfollowData)
    f.save()
    user_id = userfollowData.id 
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))


def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow.objects.get(user=currentUser, user_follower=userfollowData)
    f.delete()
    user_id = userfollowData.id 
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
