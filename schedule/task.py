from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .models import Ticket

@shared_task
def send_event_reminder(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        user_email = ticket.email
        event_name = ticket.event.name
        event_date = ticket.event.date
        user_name = ticket.name

        send_mail(
            'Event Reminder',
            f'Dear {user_name},\n\nThis is a reminder for the event "{event_name}" happening on {event_date}.\n\nThank you!',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    except Ticket.DoesNotExist:
        # Handle the case where the ticket does not exist
        pass
