from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.db.models import Count
from .models import Tweet, Comment, Like
from .forms import TweetForm, CommentForm, UserRegistrationForm,UserLoginForm

from django.contrib.auth.views import LoginView
 

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = UserLoginForm




def home(request):
    latest_tweets = Tweet.objects.all().order_by('-created_at')[:5]
    trending_tweets = Tweet.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:5]
    top_users = Tweet.objects.values('user__username').annotate(tweet_count=Count('id')).order_by('-tweet_count')[:5]

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TweetForm(request.POST, request.FILES)
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                return redirect('home')
        else:
            form = TweetForm()
    else:
        form = None

    context = {
        'latest_tweets': latest_tweets,
        'trending_tweets': trending_tweets,
        'top_users': top_users,
        'form': form
    }
    return render(request, 'home.html', context)

def tweet_list(request):
    tweets = Tweet.objects.all().order_by("-created_at")
    return render(request, "tweet_list.html", {"tweets": tweets})

def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    comments = tweet.comments.all().order_by('-created_at')
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.tweet = tweet
                comment.save()
                return redirect('tweet_detail', tweet_id=tweet.id)
        else:
            form = CommentForm()
    else:
        form = None
    return render(request, "tweet_detail.html", {"tweet": tweet, "comments": comments, "form": form})

@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect("tweet_list")
    else:
        form = TweetForm()
    return render(request, "tweet_form.html", {"form": form})

@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect("tweet_list")
    else:
        form = TweetForm(instance=tweet)
    return render(request, "tweet_form.html", {"form": form})

@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == "POST":
        tweet.delete()
        return redirect("tweet_list")
    return render(request, "tweet_confirm_delete.html", {"tweet": tweet})

@login_required
def like_tweet_ajax(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
    if not created:
        like.delete()
    return JsonResponse({'likes_count': tweet.total_likes()})

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data["password1"])
            user.save()
            
            authenticated_user = authenticate(username=user.username, password=form.cleaned_data["password1"])
            if authenticated_user:
                login(request, authenticated_user)
                return redirect("home")
    else:
        form = UserRegistrationForm()
    
    return render(request, "registration/register.html", {"form": form})
