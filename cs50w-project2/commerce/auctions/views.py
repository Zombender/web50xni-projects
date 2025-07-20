from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (ListView, CreateView, DetailView, UpdateView)

from .models import User, Listing, Bid, Comment, Category
from .forms import ListingForm, BidForm


def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('index')

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class HomeListingView(LoginRequiredMixin, ListView):
    model = Listing
    template_name = 'auctions/index.html'
    context_object_name = 'listings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listings = context.get('listings')
        for listing in listings:
            listing.is_watched = listing.is_watched_by(user=self.request.user)
        return context

    def get_queryset(self):
        return Listing.objects.order_by('-is_active', '-date_posted')


class CreateListingView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'auctions/create-listing.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DetailListingView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Listing
    template_name = 'auctions/listing.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        listing = self.get_object()
        user = self.request.user
        context['is_watched_by_user'] = False if listing.is_watched_by(user) else True
        context['is_user_listing'] = listing.author == user
        return context

    def test_func(self):
        listing = self.get_object()
        if listing.author == self.request.user:
            return True
        return False


class UpdateListingView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    template_name = 'auctions/edit-listing.html'
    form_class = ListingForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        listing = self.get_object()
        if listing.author == self.request.user:
            return True
        return False


@login_required
def toggle_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    user = request.user

    if listing.is_watched_by(user):
        listing.watchlist.remove(user)
    else:
        listing.watchlist.add(user)

    return redirect('listing', pk=pk)


class CreateBidView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Bid
    template_name = 'auctions/add-bid.html'
    form_class = BidForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['listing'] = get_object_or_404(Listing, pk=self.kwargs['pk'])
        return kwargs

    def test_func(self):
        listing = get_object_or_404(Listing, pk=self.kwargs['pk'])
        return listing.author != self.request.user

    def handle_no_permission(self):
        return redirect('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        listing_id = self.kwargs['pk']
        listing = get_object_or_404(Listing, pk=listing_id)
        form.instance.listing = listing

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('listing', kwargs={'pk': self.kwargs['pk']})


class WatchlistView(LoginRequiredMixin, ListView):
    model = Listing
    template_name = 'auctions/watchlist.html'
    context_object_name = 'listings'

    def get_queryset(self):
        return self.request.user.watchlist.all()


class CategoryListview(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'auctions/category.html'
    context_object_name = 'categories'


class CategoryListingListView(LoginRequiredMixin, ListView):
    model = Listing
    template_name = 'auctions/category-listing.html'
    context_object_name = 'listings'

    def get_queryset(self):
        category_id = self.kwargs['pk']
        return Listing.objects.filter(category__pk=category_id, is_active=True)

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['pk']
        category = get_object_or_404(Category, pk=category_id)
        context['category'] = category
        return context
