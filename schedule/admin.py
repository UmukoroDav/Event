from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Speaker)
admin.site.register(Day)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Payment)
admin.site.register(Gallery)
admin.site.register(Faq)
admin.site.register(CustomUser)

class VenueGalleryInline(admin.TabularInline):
    model = VenueGallery
    extra = 1

class VenueAdmin(admin.ModelAdmin):
    inlines = [VenueGalleryInline]

admin.site.register(Venue, VenueAdmin)
