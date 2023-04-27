from django.db import models
from django.utils import timezone
from tinymce import models as tinymce_models
import datetime


class Events(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Наименование мероприятия"
    )
    
    image = models.ImageField(
        upload_to="events_images", verbose_name="Изображение мероприятия",
        blank=True, null=True
    )
    
    is_public = models.BooleanField(
        default=True, verbose_name="Публичное ли мероприятие"
    )
    
    short_information = models.TextField(
        max_length=200, blank=True, null=True,
        verbose_name="Краткая информация о мероприятии"
    )
    
    full_information = tinymce_models.HTMLField(
        blank=True, null=True,
        verbose_name="Полная информация о мероприятии",
    )
    
    registered_visitors = models.PositiveIntegerField(
        verbose_name="Текущее кол-во записавшихся посетителей", default=0
    )
    
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
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        if self.registered_visitors >= self.max_visitors:
            self.registered_visitors = self.max_visitors
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'мероприятие'
        verbose_name_plural = 'Мероприятия'