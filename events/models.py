from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from tinymce import models as tinymce_models
from shortuuid.django_fields import ShortUUIDField
import datetime

events_images_folder_path = "events_images/"

placeholder_image_path = events_images_folder_path + "placeholder.jpg"


class EventVenues(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Наименование места проведения мероприятия"
    )
    
    address = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="Адрес места проведения мероприятия"
    )
    
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True,
        verbose_name="Координата широты для места проведения мероприятия"
    )
    
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True,
        verbose_name="Координата долготы для места проведения мероприятия"
    )
    
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания места проведения мероприятия"
    )
    
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления места проведения мероприятия"
    )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'место проведения мероприятия'
        verbose_name_plural = 'Места проведения мероприятий'
        
        
class EventTypes(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Наименование типа мероприятия"
    )
    
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания типа мероприятия"
    )
    
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления типа мероприятия"
    )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'тип мероприятия'
        verbose_name_plural = 'Типы мероприятий'        
        

class AbstractEvents(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Наименование мероприятия"
    )
    
    image = models.ImageField(
        upload_to=events_images_folder_path, verbose_name="Изображение для мероприятия",
        blank=True, null=True, default=placeholder_image_path
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
    
    def visitors_len(self):
        return self.visitors.count()
    
    def end_datetime(self):
        return self.start_datetime + self.duration
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        #if self.registered_visitors >= self.max_visitors:
            #self.registered_visitors = self.max_visitors
        if self.closing_registration_date >= self.start_datetime:
            self.closing_registration_date = self.start_datetime
        if not self.image:
            self.image = placeholder_image_path
        super().save(*args, **kwargs)
    
    class Meta:
        abstract = True
        
        
class Events(AbstractEvents):
    venue_id = models.ForeignKey(
        EventVenues, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="Место проведения мероприятия"
    )
    
    category_id = models.ForeignKey(
        EventTypes, on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Тип мероприятия"
    )
    
    visitors = models.ManyToManyField(
        get_user_model(), blank=True, through="EventRegistrations",
        verbose_name="Зарегестрированные на мероприятие пользователи",
    )
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'мероприятие'
        verbose_name_plural = 'Мероприятия'
        

class PrivateEvents(AbstractEvents):
    venue_id = models.ForeignKey(
        EventVenues, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="Место проведения приватного мероприятия"
    )
    
    category_id = models.ForeignKey(
        EventTypes, on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Тип приватного мероприятия"
    )
    
    visitors = models.ManyToManyField(
        get_user_model(), blank=True, through="PrivateEventRegistrations",
        verbose_name="Зарегестрированные на приватное мероприятие пользователи",
    )
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'приватное мероприятие'
        verbose_name_plural = 'Приватные мероприятия'


class AbstractEventRegistrations(models.Model):
    
    shortuuid = ShortUUIDField(
        auto_created=True,
        alphabet="0123456789",
        unique=True,
        verbose_name="UUID записи на мероприятие",
        length=10,
        max_length=10,
    )
    
    is_invitation_accepted = models.BooleanField(
        default=False, blank=True, null=True,
        verbose_name="Принял ли пользователь приглашение на мероприятие"
    )
    
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации на мероприятие"
    )
    
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления регистрации на мероприятие"
    )
    
    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        abstract = True


class EventRegistrations(AbstractEventRegistrations):
    
    event_id = models.ForeignKey(
        Events, on_delete=models.CASCADE,
        verbose_name="ID мероприятия"
    )
    
    user_id = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        verbose_name="ID пользователя"
    )
    
    def __str__(self):
        return f"Запись на мероприятие №{self.shortuuid}, ID мероприятия - {self.event_id}, ID мользователя - {self.user_id}"
    
    class Meta:
        verbose_name = 'регистрацию на мероприятие'
        verbose_name_plural = 'Регистрации на мероприятия'
        unique_together = ('event_id', 'user_id')
        constraints = [
            models.UniqueConstraint(fields=unique_together, name='event_user_id_unique'),
        ]


class PrivateEventRegistrations(AbstractEventRegistrations):
    
    private_event_id = models.ForeignKey(
        PrivateEvents, on_delete=models.CASCADE,
        verbose_name="ID приватного мероприятия"
    )
    
    user_id = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        verbose_name="ID пользователя"
    )
    
    def __str__(self):
        return f"Запись на приватное мероприятие №{self.shortuuid}, ID мероприятия - {self.event_id}, ID мользователя - {self.user_id}"
    
    class Meta:
        verbose_name = 'регистрацию на приватное мероприятие'
        verbose_name_plural = 'Регистрации на приватные мероприятия'
        unique_together = ('private_event_id', 'user_id')
        constraints = [
            models.UniqueConstraint(fields=unique_together, name='private_event_user_id_unique'),
        ]