from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    profile = models.ImageField(default='avatar.svg')
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name



class Speaker(models.Model):
    Profile = models.ImageField(upload_to='static/image')
    Name = models.CharField(max_length=100)
    Position = models.CharField(max_length=100)
    twitter = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    linkden = models.URLField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Name


class Day(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Venue(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    map_embed_url = models.URLField(max_length=400)

    def __str__(self):
        return self.name

class VenueGallery(models.Model): 
    venue = models.ForeignKey(Venue, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='venue_gallery/')

    def __str__(self):
        return f"Gallery image for {self.venue.name}"

class Event(models.Model):
    day = models.ForeignKey(Day, related_name='events', on_delete=models.CASCADE)
    time = models.TimeField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    speaker_name = models.ForeignKey(Speaker, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(default='1')
    # speaker_profile_url = models.URLField(blank=True, null=True)
    venue = models.ForeignKey(Venue,  on_delete=models.CASCADE, default=1, null=True, blank=True)

    def __str__(self):
        return self.title

class Ticket(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    features = models.JSONField()
    event = models.ForeignKey(Event, related_name='tickets', on_delete=models.CASCADE)
    is_free = models.BooleanField(default=False)
    # is_statndard = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Payment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    reference = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.reference


class Gallery(models.Model):
    profile = models.ImageField(upload_to='static/image')


class Faq(models.Model):
    qusetion = models.CharField(max_length=100)
    answer = models.TextField()

    def __str__(self):
        return self.qusetion



