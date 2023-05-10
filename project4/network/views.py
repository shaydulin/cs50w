from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.forms import ModelForm, Textarea
from django.contrib import messages
import json


# form for adding post
class AddPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        labels = {
            "content": "",
        }
        widgets = {
            "content": Textarea(attrs={'autofocus': True}),
        }


@csrf_exempt
@login_required
def like_post(request):
    
    if request.method != "PATCH":
        return JsonResponse({"error": "PATCH request required."}, status=400)

    try:
        # check if there is info about post in request
        data = json.loads(request.body)
        post_id = data.get("id")
        post = Post.objects.get(pk=post_id)
        # check if post already liked; like if not and unlike if does
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
    except Exception:
        return JsonResponse({"error": "Something wrong."}, status=400)

    # return data for changing html via js
    return JsonResponse({
        "success": True,
        "likes_count": post.likes.count(),
        "liked": liked
        }, status=200)


@csrf_exempt
@login_required
def edit_post(request):
    if request.method != "PATCH":
        return JsonResponse({"error": "PATCH request required."}, status=400)

    try:
        # chef if there data in request
        data = json.loads(request.body)
        post_id = data.get("id")
        new_content = data.get("new_content")
        post = Post.objects.get(pk=post_id)

        # user can't edit someone else's post
        if post.poster != request.user:
            return JsonResponse({"error": "Forbidden"}, status=400)
        post.content = new_content
        post.save()
    except Exception:
        return JsonResponse({"error": "Something wrong."}, status=400)

    # if ok return success
    return JsonResponse({"success": True}, status=200)


@csrf_exempt
@login_required
def add_post(request):
    if request.method != 'POST':
        messages.error(request, 'POST request required.')
        return HttpResponseRedirect(reverse('index'))

    form = AddPostForm(request.POST)
    try:
        # check if post can be added
        post = form.save(commit=False)
        post.poster = request.user
        post.save()
        # return error if not
    except ValueError:
        messages.error(request, 'Something wrong.')
        return HttpResponseRedirect(reverse('index'))
    except IntegrityError:
        messages.error(request, 'Something wrong.')
        return HttpResponseRedirect(reverse('index'))
    
    # return success if yes
    messages.success(request, 'Post added.')
    return HttpResponseRedirect(reverse('index'))


@csrf_exempt
@login_required
def follow_user(request, id):

    if request.method != 'POST':
        return JsonResponse({
            "error": "POST request required."
        })

    try:
        person = User.objects.get(pk=id)
        # check if user tries to follow himself
        if person == request.user:
            return JsonResponse({
                "error": "Cannot follow yourself"
            })

        if person.followers.filter(id=request.user.id).exists():
            person.followers.remove(request.user.id)
            follow_btn = 'Follow'
        else:
            person.followers.add(request.user.id)
            follow_btn = 'Unfollow'

        followers_count = person.followers.count()

        # if ok return data for changing html
        return JsonResponse({
            'followers_count': followers_count,
            'follow_btn': follow_btn,
        })

    except Exception:
        return JsonResponse({
            "error": "Something wrong."
        })


def index(request):

    # show posts; and likes if user authenticated
    if request.user.is_authenticated:
        posts = Post.objects.annotate(
                    likes_count=Count('likes'), liked=Count('likes', filter=Q(likes=request.user))
                ).order_by(
                    "-add_date"
                )

    else:
        posts = Post.objects.annotate(
                    likes_count=Count('likes')
                ).order_by(
                    "-add_date"
                )

    # return post, 10 posts per page
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "title": "All posts",
        'form': AddPostForm(),
    })


@login_required
def following(request):

    # same as above but only posts from following users
    user = request.user.id
    posts = Post.objects.filter(
                poster__in=User.objects.filter(followers=user)
            ).annotate(
                likes_count=Count('likes'), liked=Count('likes', filter=Q(likes=request.user))
            ).order_by("-add_date")

    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "title": "Following",
    })


def user_profile(request, id):
    
    person = User.objects.get(pk=id)

    followers_count = person.followers.count()
    followings_count = person.followings.count()
    user_follows = person.followers.filter(id=request.user.id).exists()

    if request.user.is_authenticated:

        posts = person.posts.annotate(
                    likes_count=Count('likes'), liked=Count('likes', filter=Q(likes=request.user))
                ).order_by(
                    "-add_date"
                )

    else:

        posts = person.posts.annotate(
                    likes_count=Count('likes')
                ).order_by(
                    "-add_date"
                )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'network/user-profile.html', {
        'person': person,
        'followers_count': followers_count,
        'followings_count': followings_count,
        'page_obj': page_obj,
        'user_follows': user_follows,
    })


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
