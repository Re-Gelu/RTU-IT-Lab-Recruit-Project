from datetime import timedelta
from celery import shared_task
from django.db.models import Q
from django.core import mail
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from config.qiwi import get_QIWI_p2p

from .models import EventRegistrations, PrivateEventRegistrations, PaidEventRegistrations, Events


payment_statuses = PaidEventRegistrations.PaymentStatuses
notification_days_before_events = getattr(settings, "NOTIFICATION_DAYS_BEFORE_EVENTS", None)


@shared_task
def payment_handler():
    result = ""
    p2p = get_QIWI_p2p()
    if p2p != None and PaidEventRegistrations.objects.filter(Q(payment_status=payment_statuses.CREATED) | Q(payment_status=payment_statuses.WAITING)).exists():
        for registration in PaidEventRegistrations.objects.filter(Q(payment_status=payment_statuses.CREATED) | Q(payment_status=payment_statuses.WAITING)):
            payment_status = p2p.check(registration.shortuuid).status
            if registration.payment_status != payment_status:
                result += f'\nRegistration payment with id: {registration.shortuuid} have new payment status {registration.payment_status} -> {payment_status}. '
                registration.payment_status = payment_status
                registration.save()
            if payment_status in (payment_statuses.REJECTED, payment_statuses.EXPIRED):
                p2p.reject(registration.shortuuid)
                result += f'Registration payment with id: {registration.shortuuid} have been deleted. '
        return result if result != "" else "Waiting for new payment statuses..."
    else:
        return "No payments to handle for now..."
    
@shared_task
def send_registration_reminder():
    assert notification_days_before_events is not None, (f"Set NOTIFICATION_DAYS_BEFORE_EVENTS setting!")
    
    for days in notification_days_before_events:
        date_to_check = timezone.now() + timedelta(days=days)
        registrations = EventRegistrations.objects.filter(event_id__start_datetime__date=date_to_check)
        for registration in registrations:
            user = registration.user_id
            event = registration.event_id
            subject = f'Registration reminder for {event.name} with №{registration.shortuuid}'
            message = f'{user.username}, you are registered for {event.name} in {days} days.'
            send_mail(subject, message, settings.DEFAULT_EMAIL_FROM, [user.email])