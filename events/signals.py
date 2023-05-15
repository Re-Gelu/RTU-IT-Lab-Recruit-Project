from django.db.models import signals
from django.dispatch import receiver

from .models import (EventRegistrations, Events, PaidEventRegistrations,
                     PaidEvents, PrivateEventRegistrations, PrivateEvents)
from .tasks import (notify_event_cancellation, notify_paid_event_cancellation,
                    notify_private_event_cancellation,
                    send_paid_registration_delete_notification,
                    send_paid_registration_notification,
                    send_private_registration_delete_notification,
                    send_private_registration_notification,
                    send_registration_delete_notification,
                    send_registration_notification)

# Tasks based on model signals 


# Sending email notification when user registered for the event

@receiver(signals.post_save, sender=EventRegistrations)
def EventRegistrations_post_save(sender, instance, created, **kwargs):
    if created and instance.is_invitation_accepted: # object is being created
        send_registration_notification.delay(
            event_name=instance.event.name,
            registration_shortuuid=instance.shortuuid,
            user_email=instance.user.email
        )
        
@receiver(signals.post_save, sender=PrivateEventRegistrations)
def PrivateEventRegistrations_post_save(sender, instance, created, **kwargs):
    if instance.is_invitation_accepted:
        send_private_registration_notification.delay(
            event_name=instance.event.name,
            registration_shortuuid=instance.shortuuid,
            user_email=instance.user.email
        )
        
@receiver(signals.post_save, sender=PaidEventRegistrations)
def PaidEventRegistrations_post_save(sender, instance, created, **kwargs):
    if instance.is_invitation_accepted and instance.payment_status == instance.PaymentStatuses.PAID:
        send_paid_registration_notification.delay(
            event_name=instance.event.name,
            registration_shortuuid=instance.shortuuid,
            user_email=instance.user.email
        )


# Sending email notification when user delete registration for the event

@receiver(signals.post_delete, sender=EventRegistrations)
def EventRegistrations_post_delete(sender, instance, **kwargs):
    send_registration_delete_notification.delay(
        event_name=instance.event.name,
        registration_shortuuid=instance.shortuuid,
        user_email=instance.user.email
    )
        
@receiver(signals.post_delete, sender=PrivateEventRegistrations)
def PrivateEventRegistrations_post_delete(sender, instance, **kwargs):
    send_private_registration_delete_notification.delay(
        event_name=instance.event.name,
        registration_shortuuid=instance.shortuuid,
        user_email=instance.user.email
    )
        
@receiver(signals.post_delete, sender=PaidEventRegistrations)
def PaidEventRegistrations_post_delete(sender, instance, **kwargs):
    send_paid_registration_delete_notification.delay(
        event_name=instance.event.name,
        registration_shortuuid=instance.shortuuid,
        user_email=instance.user.email
    )
        
        
# Sending email notification of deleting the event

@receiver(signals.post_delete, sender=Events)
def Events_post_save(sender, instance, **kwargs):
    notify_event_cancellation.delay(
        event_name=instance.name,
        recipients=[registration.user.email for registration in EventRegistrations.objects.filter(event=instance.id, is_invitation_accepted=True)]
    )
        
@receiver(signals.post_delete, sender=PrivateEvents)
def PrivateEvents_post_save(sender, instance, **kwargs):
    notify_private_event_cancellation.delay(
        event_name=instance.name,
        recipients=[registration.user.email for registration in PrivateEventRegistrations.objects.filter(event=instance.id, is_invitation_accepted=True)]
    )
        
@receiver(signals.post_delete, sender=PaidEvents)
def PaidEvents_post_save(sender, instance, **kwargs):
    notify_paid_event_cancellation.delay(
        event_name=instance.name,
        recipients=[registration.user.email for registration in PaidEventRegistrations.objects.filter(event=instance.id, is_invitation_accepted=True, payment_status="PAID")]
    )