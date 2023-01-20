from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class Organization(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=35)
    description = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    joined_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organization'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Organization, self).save(*args, **kwargs)

    @property
    def cameras(self):
        return self.camera_set.all()

    def species(self):
        Specie = apps.get_model('core', 'Specie')
        return Specie.objects.filter(enabled=True).all()


class User(AbstractUser):
    email = models.EmailField('email address', unique=True, help_text='Required, Add a valid email address')
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    @property
    def camera(self):
        return self.camera_set.first()
