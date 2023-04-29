from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from tinymce import models as tinymce_models
import datetime

events_images_folder_path = "events_images/"
placeholder_image_path = events_images_folder_path + "placeholder.jpg"


class Events(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Наименование мероприятия"
    )
    
    image = models.ImageField(
        upload_to=events_images_folder_path, verbose_name="Изображение для мероприятия",
        blank=True, null=True, default=placeholder_image_path
    )
    
    venue = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="Место проведения мероприятия"
    )
    
    start_datetime = models.DateTimeField(
        verbose_name="Время проведения мероприятия",
    )
    
    duration = models.DurationField(
        blank=True, null=True, default=datetime.timedelta(hours=2),
        max_length=datetime.timedelta(days=31),
        verbose_name="Длительность мероприятия",
    )
    
    closing_registration_date = models.DateTimeField(
        verbose_name="Время закрытия регистрации на мероприятие",
    )
    
    short_information = models.TextField(
        max_length=200, blank=True, null=True,
        verbose_name="Краткая информация о мероприятии"
    )
    
    full_information = tinymce_models.HTMLField(
        blank=True, null=True,
        verbose_name="Полная информация о мероприятии",
    )
    
    """ visitors_list = models.JSONField(
        editable=False,
        blank=True, null=True,
        auto_created=True, default=list,
        verbose_name="Зарегестрированные посетители мероприятия"
    ) """
    
    max_visitors = models.PositiveIntegerField(
        verbose_name="Максимум посетителей", default=0
    )
    
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата добавления мероприятия"
    )
    
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления мероприятия"
    )

    def was_publiched_recently(self):
        return self.created >= timezone.now() - datetime.timedelta(days=7)
    
    def end_datetime(self):
        return self.date + self.duration
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        if self.registered_visitors >= self.max_visitors:
            self.registered_visitors = self.max_visitors
        if self.closing_registration_date >= self.date:
            self.closing_registration_date = self.date
        if not self.image:
            self.image = placeholder_image_path
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'мероприятие'
        verbose_name_plural = 'Мероприятия'
        

class PrivateEvents(Events):
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'приватное мероприятие'
        verbose_name_plural = 'Приватные мероприятия'
        

class EventsRegistrations(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации на мероприятие"
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления регистрации на мероприятие"
    )