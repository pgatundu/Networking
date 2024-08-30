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
from django.views.decorators.csrf import csrf_exempt
from .models import User,Post,Follow,Like

register = template.Library()

def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        return JsonResponse({'status': 'Post deleted successfully'})
    return JsonResponse({'status': 'Invalid request'}, status=400)



                        
def edit(request,post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change Successful", "data": data["content"]})

def index(request):
    allPosts = Post.objects.all().order_by("-id")

    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    like_counts = {}
    for post in allPosts:
        like_counts[post.id] = post.likes.filter(liked=True).count()

    allLikes = Like.objects.all()
    whoYouLiked = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)
    except:
        whoYouLiked = []

    return render(request, "network/index.html", {
        "allPosts": allPosts,
        "posts_of_the_page": posts_of_the_page,
        "whoYouLiked": whoYouLiked,
        "like_counts": like_counts
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

  try:
      checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
      if len(checkFollow) != 0:
          isFollowing = True
      else:
          isFollowing = False
      
  except:
      isFollowing = False

  # Paginator
  paginator = Paginator(allPosts, 10)
  page_number = request.GET.get('page')
  posts_of_the_page = paginator.get_page(page_number)
  return render(request, "network/profile.html",{
                    "allPosts": allPosts,
                    "posts_of_the_page": posts_of_the_page,
                    "username": user.username,
                    "following": following,
                    "followers": followers,
                    "isFollowing": isFollowing,
                    "user_profile": user
                })


def toggle_like(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        user = request.user
        post = Post.objects.get(id=post_id)

        if action == 'like':
            like, created = Like.objects.get_or_create(post=post, user=user)
            if not created:
                return JsonResponse({'success': False, 'error': 'Already liked'})
        elif action == 'unlike':
            Like.objects.filter(post=post, user=user).delete()
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})

        like_count = post.likes.filter(liked=True).count()
        return JsonResponse({'success': True, 'like_count': like_count})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    followingPeople = Follow.objects.filter(user=currentUser)
    allPosts = Post.objects.all().order_by('id').reverse()

    follwingPosts =[]
    for post in allPosts:
        for person in followingPeople:
            if person.user_follower == post.user:
                follwingPosts.append(post)

     # Paginator
    paginator = Paginator(follwingPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)
    return render(request, "network/following.html",{
                      "posts_of_the_page": posts_of_the_page
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



def get_item(dictionary, key):
    return dictionary.get(key)

