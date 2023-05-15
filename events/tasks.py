from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from config.qiwi import get_QIWI_p2p

from .models import EventRegistrations, PaidEventRegistrations

payment_statuses = PaidEventRegistrations.PaymentStatuses

notification_days_before_events = getattr(settings, "NOTIFICATION_DAYS_BEFORE_EVENTS", None)


# Tasks

@shared_task
def payment_handler():
    """Обработчик платежей QIWI"""
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
    """Уведомление о предстоящем мероприятии"""
    assert notification_days_before_events is not None, (f"Set NOTIFICATION_DAYS_BEFORE_EVENTS setting!")
    
    for days in notification_days_before_events:
        date_to_check = timezone.now() + timedelta(days=days)
        registrations = EventRegistrations.objects.filter(event__start_datetime__date=date_to_check)
        for registration in registrations:
            user = registration.user
            event = registration.event
            subject = f'Напоминание о регистрации на мероприятие - {event.name} c №{registration.shortuuid}'
            message = f"""
                Здравствуйте! 
                Вы зарегистрированы на мероприятие - {event.name}, которое пройдет через {days} дней. 
                Ждем Вас на мероприятии!
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            

# Sending email notification when user registered for the event

@shared_task
def send_registration_notification(event_name, registration_shortuuid, user_email):
    """Уведомление пользователя о том что он зарегестрировался на мероприятие """
    subject = f'Уведомление о регистрации на мероприятие - {event_name} c №{registration_shortuuid}'
    message = f"""
        Здравствуйте! Вы успешно зарегистрировались на мероприятие - {event_name}.
        Номер вашей регистрации - {registration_shortuuid}.
        Спасибо за участие!
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
    

@shared_task
def send_private_registration_notification(event_name, registration_shortuuid, user_email):
    """Уведомление пользователя о том что он зарегестрировался на приватное мероприятие"""
    subject = f'Уведомление о регистрации на приватное мероприятие - {event_name} c №{registration_shortuuid}'
    message = f"""
        Здравствуйте! Вы успешно зарегистрировались на приватное мероприятие - {event_name}.
        Номер вашей регистрации - {registration_shortuuid}.
        Спасибо за участие!
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
    
    
@shared_task
def send_paid_registration_notification(event_name, registration_shortuuid, user_email):
    """Уведомление пользователя о том что он зарегестрировался на платное мероприятие"""
    subject = f'Уведомление о регистрации на платное мероприятие - {event_name} c №{registration_shortuuid}'
    message = f"""
        Здравствуйте! Вы успешно зарегистрировались на платное мероприятие - {event_name}.
        Номер вашей регистрации - {registration_shortuuid}.
        Спасибо за участие!
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])


# Sending email notification when user deleted registration for the event

@shared_task
def send_registration_delete_notification(event_name, registration_shortuuid, user_email):
    """Уведомление пользователя о том что он удалил регистрацию на мероприятие"""
    subject = f'Уведомление о удалении регистрации на мероприятие - {event_name} c №{registration_shortuuid}'
    message = f"""
        Здравствуйте! Ваша регистрация на мероприятие - {event_name} была удалена.
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
    

@shared_task
def send_private_registration_delete_notification(event_name, registration_shortuuid, user_email):
    """Уведомление пользователя о том что он удалил регистрацию на приватное мероприятие"""
    subject = f'Уведомление о удалении регистрации на приватное мероприятие - {event_name} c №{registration_shortuuid}'
    message = f"""
        Здравствуйте! Ваша регистрация на приватное мероприятие - {event_name} была удалена.
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
    
    
@shared_task
def send_paid_registration_delete_notification(event_name, registration_shortuuid, user_email):
    """Уведомление пользователя о том что он удалил регистрацию на платное мероприятие"""
    subject = f'Уведомление о удалении регистрации на платное мероприятие - {event_name} c №{registration_shortuuid}'
    message = f"""
        Здравствуйте! Ваша регистрация на платное мероприятие - {event_name} была удалена.
        Деньги за мероприятие будут возвращены на Ваш счет в ближайшее время!
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])    


# Sending email notification when the event is unavailable

@shared_task
def notify_event_cancellation(event_name, recipients):
    """Уведомление об отмене мероприятия"""
    subject = f"Мероприятие {event_name} отменено!"
    message = f"""
        Сообщаем вам, что мероприятие - {event_name}, на которое вы зарегистрировались, было отменено. 
        Пожалуйста, обратитесь к организаторам мероприятия за дополнительной информацией. 
        :(
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipients)
    

@shared_task
def notify_private_event_cancellation(event_name, recipients):
    """Уведомление об отмене приватного мероприятия"""
    subject = f"Приватное мероприятие {event_name} отменено!"
    message = f"""
        Сообщаем вам, что приватное мероприятие - {event_name}, на которое вы зарегистрировались, было отменено. 
        Пожалуйста, обратитесь к организаторам мероприятия за дополнительной информацией. 
        :(
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipients)
    

@shared_task
def notify_paid_event_cancellation(event_name, recipients):
    """Уведомление об отмене платного мероприятия"""
    subject = f"Платное мероприятие {event_name} отменено!"
    message = f"""
        Сообщаем вам, что платное мероприятие - {event_name}, на которое вы зарегистрировались, было отменено.
        Деньги за мероприятие будут возвращены на Ваш счет в ближайшее время!
        Пожалуйста, обратитесь к организаторам мероприятия за дополнительной информацией. 
        :(
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipients)