from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from paystackapi.paystack import Paystack
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from datetime import datetime, timedelta
from .task import send_event_reminder
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import *

paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)


# Create your views here.
# @login_required(login_url='applogin')
def index(request):
    speaker = Speaker.objects.all()
    days = Day.objects.prefetch_related('events').all()
    tickets = Ticket.objects.all()
    gallery = Gallery.objects.all()
    faq = Faq.objects.all()
    venues = Venue.objects.prefetch_related('gallery').all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        email_subject = f'New Message From {name}'
        email_body = f'You have reached a new message from {name}\n\n Subject: {subject}\n\n Email: {email} \n\n Message: {message}'



        send_mail(
            email_subject,
            email_body,
            'davidogheneothuke42@gmail.com',
            ['davidogheneothuke42@gmail.com'],
            fail_silently=False
        )

        messages.success(request, 'Your Email Have Been Successfully Sent!')
        return redirect('index')
    


    context = {
        'speaker':speaker,
        'days':days,
        'tickets':tickets,
        'gallery':gallery,
        'faq':faq,
        'venues': venues,
    }
    return render(request, 'index.html', context)


def ticket(request):
    tickets = Ticket.objects.all()

    context = {
        'tickets':tickets,
    }
    return render(request, 'ticket.html', context)

def applogin(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid Email and Password')
            return redirect('applogin')
    return render(request, 'login.html')

def appregister(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already Exists')
            return redirect('applogin')
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already Exists')
            return redirect('applogin')
        
        else:
            user = CustomUser(
                name=name,
                username=username,
                email=email,
            )
            user.set_password(password)
            user.save()
            login(request, user)
            return redirect('index')
    return render(request, 'register.html')

        
def edituser(request):
    user = request.user
    edituser = EditUser(instance=user)

    if request.method == 'POST':
        edituser = EditUser(request.POST, request.FILES, instance=user)
        if edituser.is_valid():
            edituser.save()
            # messages.success(request, 'This user was updated successfully')
            return redirect('index')

    context = {
        'edituser':edituser,
    }
    return render(request, 'editprofile.html', context)


def applogout(request):
    logout(request)
    return redirect('index')



def initiate_payment(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        amount = int(ticket.price * 100)  # Paystack expects the amount in kobo
        payment_url = 'https://api.paystack.co/transaction/initialize'
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': email,
            'amount': amount,
            'callback_url': request.build_absolute_uri('/verify_payment'),
            'metadata': {
                'ticket_id': ticket_id,
                'name': name,
                'email': email
            }
        }
        response = requests.post(payment_url, json=data, headers=headers)
        res_data = response.json()
        if res_data['status']:
            return redirect(res_data['data']['authorization_url'])
        else:
            return JsonResponse(res_data, status=400)
    return render(request, 'buy_ticket.html', {'ticket': ticket})

@csrf_exempt
def verify_payment(request):
    if request.method == 'GET':
        reference = request.GET.get('reference')
        if not reference:
            return render(request, 'payment_failed.html', {'error': 'No reference provided'})

        payment_url = f'https://api.paystack.co/transaction/verify/{reference}'
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        
        try:
            response = requests.get(payment_url, headers=headers)
            res_data = response.json()

            if res_data.get('status', False):
                # Retrieve ticket ID from the metadata
                metadata = res_data['data'].get('metadata', {})
                ticket_id = metadata.get('ticket_id')
                user_email = metadata.get('email')
                user_name = metadata.get('name')

                if not ticket_id:
                    messages.error(request,  "No ticket ID in metadata")
                    return render(request, 'payment_failed.html', {'error': 'No ticket ID in metadata'})

                # Mark the ticket as paid
                try:
                    ticket = Ticket.objects.get(id=ticket_id)
                    ticket.is_paid = True
                    ticket.save()
                    messages.success(request,  f"Ticket {ticket_id} marked as paid")

                    # Calculate amount in dollars
                    amount_in_dollars = res_data['data']['amount'] / 100  # Convert amount to dollars

                    payment = Payment.objects.create(
                        ticket=ticket,
                        amount=amount_in_dollars,
                        email=user_email,
                        reference=reference,
                        verified=True
                    )
                    payment.save()
                    messages.success(request,  f"Payment record created for ticket {ticket_id}")

                    # Send initial confirmation email
                    send_mail(
                        'Ticket Purchase Confirmation',
                        f'Dear {user_name},\n\nYour payment for the ticket (ID: {ticket_id}) was successful.\n\nThank you for your purchase!',
                        settings.DEFAULT_FROM_EMAIL,
                        [user_email],
                        fail_silently=False,
                    )

                    # Schedule event reminder email
                    event_date = ticket.event.date
                    reminder_time = event_date - timedelta(days=3)  # Send reminder 1 day before the event
                    send_event_reminder.apply_async((ticket_id,), eta=reminder_time)

                    return render(request, 'payment_success.html', {'result': amount_in_dollars})
                except Ticket.DoesNotExist:
                    return render(request, 'payment_failed.html', {'error': 'Ticket does not exist'})
            else:
                return render(request, 'payment_failed.html', {'error': res_data.get('message', 'Unknown error')})

        except requests.exceptions.RequestException as e:
            return render(request, 'payment_failed.html', {'error': f'Error communicating with Paystack: {str(e)}'})

    return render(request, 'payment_failed.html', {'error': 'Invalid request'})
   

#    xwdl fogc acjg cyad