import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
from tinymce import models as tinymce_models

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
        if self.closing_registration_date and self.start_datetime and self.closing_registration_date >= self.start_datetime:
            self.closing_registration_date = self.start_datetime
        if not self.image:
            self.image = placeholder_image_path
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Events(AbstractEvents):
    venue = models.ForeignKey(
        EventVenues, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="Место проведения мероприятия"
    )

    category = models.ForeignKey(
        EventTypes, on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Тип мероприятия"
    )

    visitors = models.ManyToManyField(
        get_user_model(),
        blank=True,
        through="EventRegistrations",
        through_fields=('event', 'user'),
        limit_choices_to={'eventregistrations__is_invitation_accepted': True},
        verbose_name="Зарегестрированные на мероприятие пользователи",
    )

    def visitors_len(self):
        return self.visitors.filter(
            eventregistrations__is_invitation_accepted=True
        ).count()

    class Meta:
        ordering = ('-id', )
        verbose_name = 'мероприятие'
        verbose_name_plural = 'Мероприятия'


class PrivateEvents(AbstractEvents):
    venue = models.ForeignKey(
        EventVenues, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="Место проведения приватного мероприятия"
    )

    category = models.ForeignKey(
        EventTypes, on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Тип приватного мероприятия"
    )

    visitors = models.ManyToManyField(
        get_user_model(), blank=True, through="PrivateEventRegistrations",
        through_fields=('event', 'user'),
        limit_choices_to={'privateeventregistrations__is_invitation_accepted': True},
        verbose_name="Зарегестрированные на приватное мероприятие пользователи",
    )

    invitation_code = ShortUUIDField(
        auto_created=True,
        alphabet="0123456789",
        unique=True,
        verbose_name="UUID код для приглашения на мероприятие",
        length=10,
        max_length=10,
    )

    def visitors_len(self):
        return self.visitors.filter(
            privateeventregistrations__is_invitation_accepted=True
        ).count()

    class Meta:
        ordering = ('-id', )
        verbose_name = 'приватное мероприятие'
        verbose_name_plural = 'Приватные мероприятия'


class PaidEvents(AbstractEvents):

    venue = models.ForeignKey(
        EventVenues, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="Место проведения платного мероприятия"
    )

    category = models.ForeignKey(
        EventTypes, on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Тип платного мероприятия"
    )

    visitors = models.ManyToManyField(
        get_user_model(), blank=True, through="PaidEventRegistrations",
        through_fields=('event', 'user'),
        limit_choices_to={'paideventregistrations__is_invitation_accepted': True,
                          'paideventregistrations__payment_status': 'PAID'},
        verbose_name="Зарегестрированные на платное мероприятие пользователи",
    )

    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Стоимость регистрации на платное мероприятие"
    )

    invitation_code = ShortUUIDField(
        auto_created=True,
        alphabet="0123456789",
        unique=True,
        verbose_name="UUID код для приглашения на мероприятие",
        length=10,
        max_length=10,
    )

    def visitors_len(self):
        return self.visitors.filter(
            paideventregistrations__is_invitation_accepted=True,
            paideventregistrations__payment_status='PAID'
        ).count()

    class Meta:
        ordering = ('-id', )
        verbose_name = 'платное мероприятие'
        verbose_name_plural = 'Платные мероприятия'



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

    event = models.ForeignKey(
        Events, on_delete=models.CASCADE,
        verbose_name="ID мероприятия"
    )

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        verbose_name="ID пользователя"
    )

    inviting_user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        blank=True, null=True, related_name='+',
        verbose_name="ID приглашающего пользователя"
    )

    def save(self, *args, **kwargs):
        if not self.inviting_user:
            self.inviting_user = self.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Запись на мероприятие №{self.shortuuid}, ID мероприятия - {self.event}, ID пользователя - {self.user}"

    class Meta:
        verbose_name = 'регистрацию на мероприятие'
        verbose_name_plural = 'Регистрации на мероприятия'
        unique_together = ('event', 'user')
        constraints = [
            models.UniqueConstraint(fields=unique_together, name='event_user_unique'),
        ]


class PrivateEventRegistrations(AbstractEventRegistrations):

    event = models.ForeignKey(
        PrivateEvents, on_delete=models.CASCADE,
        verbose_name="ID приватного мероприятия"
    )

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        verbose_name="ID пользователя"
    )

    inviting_user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        blank=True, null=True, related_name='+',
        verbose_name="ID приглашающего пользователя"
    )

    def save(self, *args, **kwargs):
        if not self.inviting_user:
            self.inviting_user = self.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Запись на приватное мероприятие №{self.shortuuid}, ID мероприятия - {self.event}, ID пользователя - {self.user}"

    class Meta:
        verbose_name = 'регистрацию на приватное мероприятие'
        verbose_name_plural = 'Регистрации на приватные мероприятия'
        unique_together = ('event', 'user')
        constraints = [
            models.UniqueConstraint(fields=unique_together, name='private_event_user_unique'),
        ]


class PaidEventRegistrations(AbstractEventRegistrations):

    class PaymentStatuses(models.TextChoices):
        CREATED = "CREATED", "Платеж создан"
        WAITING = "WAITING", "Платёж в обработке / ожидает оплаты"
        PAID = "PAID", "Платёж оплачен"
        EXPIRED = "EXPIRED", "Время жизни счета истекло. Счет не оплачен."
        REJECTED = "REJECTED", "Платёж отклонен"

    event = models.ForeignKey(
        PaidEvents, on_delete=models.CASCADE,
        verbose_name="ID платного мероприятия"
    )

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        verbose_name="ID пользователя"
    )

    inviting_user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        blank=True, null=True, related_name='+',
        verbose_name="ID приглашающего пользователя"
    )

    payment_link = models.URLField(
        verbose_name="Ссылка на оплату",
        blank=True, null=True,
    )

    payment_status = models.TextField(
        choices=PaymentStatuses.choices,
        default=PaymentStatuses.CREATED,
        verbose_name="Статус оплаты",
        blank=True, null=True,
    )

    def save(self, *args, **kwargs):
        if not self.inviting_user:
            self.inviting_user = self.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Запись на платное мероприятие №{self.shortuuid}, ID мероприятия - {self.event}, ID пользователя - {self.user}"

    class Meta:
        verbose_name = 'регистрацию на платное мероприятие'
        verbose_name_plural = 'Регистрации на платные мероприятия'
        unique_together = ('event', 'user')
        constraints = [
            models.UniqueConstraint(fields=unique_together, name='paid_event_user_unique'),
        ]