from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.forms import ModelForm, NumberInput, Textarea, URLInput, TextInput
from auctions.models import Listing, Comment, Bid
from django.db.models import Max, Count
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


from .models import User


def index(request):
    listings = Listing.objects.raw("""  SELECT * FROM auctions_listing AS l LEFT join 
                                        (SELECT listing_id, MAX(bid) AS bid FROM auctions_bid GROUP BY listing_id) AS b 
                                        ON l.id = b.listing_id
                                        WHERE l.active = True
                                        ORDER BY l.add_date DESC""")
    return render(request, "auctions/index.html", {
        "listings": listings,
        "header": "Active listings",
        "title": "Active listings"
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
            messages.success(request, f'Welcome, {user.username}.')
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, 'Invalid username and/or password.')
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out.')
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, 'Passwords must match.')
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, 'Username already taken.')
            return render(request, "auctions/register.html")
        login(request, user)
        messages.success(request, f'Welcome, {user.username}.')
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class AddListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "category", "starting_bid", "img_url", "description"]
        labels = {
            "title": _(""),
            "category": _(""),
            "starting_bid": _(""),
            "img_url": _(""),
            "description": _(""),           
        }
        widgets = {
            "title": TextInput(attrs={'placeholder': 'Title', 'autofocus': True}),
            "category": TextInput(attrs={'placeholder': 'Category'}),
            "starting_bid": NumberInput(attrs={'placeholder': 'Starting Bid'}),
            "img_url": URLInput(attrs={'placeholder': 'Image URL'}),
            "description": Textarea(attrs={'placeholder': 'Description'}),           
        }


@login_required(login_url='login')
def add_listing(request):
    if request.method == "POST":
        form = AddListingForm(request.POST)
        try:
            listing = form.save(commit=False)
            listing.creator_id = request.user.id
            listing.category = listing.category.lower()
            listing.save()
        except ValueError:
            messages.error(request, 'Something wrong.')
            return render(request, "auctions/add_listing.html", {
                "form": form
            })
        except IntegrityError:
            messages.error(request, 'Something wrong.')
            return render(request, "auctions/add_listing.html", {
                "form": form
            })
        messages.success(request, 'Listing added.')
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/add_listing.html", {
        "form": AddListingForm()
    })


class AddCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        labels = {
            "comment": _("")
        }
        widgets = {
            "comment": Textarea(attrs={'placeholder': 'Write a comment'}),
        }


class AddBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["bid"]
        labels = {
            "bid": _(""),
        }
        widgets = {
            "bid": NumberInput(attrs={'placeholder': 'Your Bid'}),
        }


def listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except ObjectDoesNotExist:
        messages.error(request, 'No such listing.')
        return HttpResponseRedirect(reverse("index"))

    comments = listing.comments.select_related('user')
    bid = listing.bids.all().order_by('-bid').first()
    creator = User.objects.get(pk=listing.creator_id)

    user_id = request.user.id
    if user_id:
        if listing.watchers.filter(id = user_id):
            button = "Remove from Watchlist"
        else:
            button = "Add to Watchlist"

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "bid": bid,
            "BidForm": AddBidForm(),
            "CommentForm": AddCommentForm(),
            "button": button,
            "creator": creator
        })

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "bid": bid,
            "BidForm": AddBidForm(),
            "CommentForm": AddCommentForm(),
            "creator": creator
        })


@login_required(login_url='login')
def comment(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        try:
            Listing.objects.get(pk=listing_id)
        except ObjectDoesNotExist:
            messages.error(request, 'No such listing.')
            return HttpResponseRedirect(reverse("index"))

        try:
            form = AddCommentForm(request.POST)
            comment = form.save(commit=False)
            comment.user_id = request.user.id
            comment.listing_id = listing_id
            comment.save()
        except ValueError:
            messages.error(request, 'Invalid comment.')
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))

        messages.success(request, 'Comment added.')    
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required(login_url='login')
def bid(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        try:
            current_bid = Bid.objects.filter(listing_id=listing_id).aggregate(Max('bid'))['bid__max']
            starting_bid = Listing.objects.get(pk=listing_id).starting_bid
        except ObjectDoesNotExist:
            messages.error(request, 'No such listing.')
            return HttpResponseRedirect(reverse("index"))


        try:
            bid = float(request.POST["bid"])
        except ValueError:
            messages.error(request, 'Invalid bid.')
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))

        if not current_bid:
            current_bid = 0

        if bid > current_bid and bid >= starting_bid:
            form = AddBidForm(request.POST)
            bid = form.save(commit=False)
            bid.user_id = request.user.id
            bid.listing_id = listing_id
            bid.save()

        else:
            messages.error(request, 'Invalid bid.')
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))

        messages.success(request, 'Bid added.')
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required(login_url='login')
def watchlist(request):
    if request.method == "POST":
        user_id = request.user.id
        listing_id = request.POST["listing_id"]
        user = User.objects.get(pk=user_id)
        try:
            listing = Listing.objects.get(pk=listing_id)
        except ObjectDoesNotExist:
            messages.error(request, 'No such listing.')
            return HttpResponseRedirect(reverse("index"))


        watch_listing = user.watchlist.filter(id=listing_id)
        if watch_listing.first() is not None:
            listing.watchers.remove(user)
            messages.success(request, 'Removed from watchlist.')
            return HttpResponseRedirect(reverse("index"))
        else:
            listing.watchers.add(user)
            messages.success(request, 'Added to watchlist.')
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    user_id = request.user.id
    watchlist = Listing.objects.raw("""  SELECT * FROM auctions_listing AS l LEFT join 
                                        (SELECT listing_id, MAX(bid) AS bid FROM auctions_bid GROUP BY listing_id) AS b 
                                        ON l.id = b.listing_id
                                        WHERE l.id IN
                                        (SELECT listing_id FROM auctions_listing_watchers WHERE user_id = %s)
                                        ORDER BY l.active DESC""", [user_id])

    return render(request, "auctions/index.html", {
        "listings": watchlist,
        "header": "Watchlist",
        "title": "Watchlist"
    })


@login_required(login_url='login')
def close_listing(request):
    if request.method == "POST":
        user_id = request.user.id
        listing_id = request.POST["listing_id"]
        try:
            listing = Listing.objects.get(pk=listing_id)
        except ObjectDoesNotExist:
            messages.error(request, 'No such listing.')
            return HttpResponseRedirect(reverse("index"))


        if user_id == listing.creator_id:
            listing.active = False
            listing.save()
            listing.watchers.clear()
            messages.info(request, 'Closed.')
            return HttpResponseRedirect(reverse("index"))

        else:
            messages.info(request, 'Forbidden.')
            return HttpResponseRedirect(reverse("index"))

    return HttpResponseRedirect(reverse("index"))


def category_view(request, category):

    listings = Listing.objects.raw("""  SELECT * FROM auctions_listing AS l LEFT join 
                                        (SELECT listing_id, MAX(bid) AS bid FROM auctions_bid GROUP BY listing_id) AS b 
                                        ON l.id = b.listing_id
                                        WHERE l.category = %s AND l.active = True""", [category.lower()])
    return render(request, "auctions/index.html", {
        "listings": listings,
        "header": f'Active Listings: category "{category}"',
        "title": category.lower()
    })


def categories(request):
    categories = Listing.objects.filter(active=True).values('category').exclude(category="").annotate(Count('category')).values('category').all()
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })