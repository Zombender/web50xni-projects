from PIL.ImageFile import ImageFile
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.core.files.images import ImageFile
from PIL import Image

import os

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Listing(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')

    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(default='default.jpg', upload_to='product-pics')
    watchlist = models.ManyToManyField(User, blank=True, related_name='watchlist')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300: # For better storage
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_absolute_url(self):
        return reverse('listing', kwargs={'pk': self.pk})

    def is_watched_by(self, user):
        return user in self.watchlist.all()

    @property
    def current_price(self):
        highest_bid = self.bids.aggregate(models.Max('amount'))['amount__max']
        return highest_bid if highest_bid is not None else self.starting_bid

    @property
    def winner(self):
        highest_bid = self.bids.order_by('-amount', '-date_posted').first()
        return highest_bid.user if highest_bid else None

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = 'bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.01)])
    date_posted = models.DateTimeField(default=timezone.now)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.TextField()

