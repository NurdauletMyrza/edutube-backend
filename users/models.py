from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, first_name, last_name, password=None, role="student", **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set."))
        if password and len(password) < 8:
            raise ValueError(_("Password must be at least 8 characters long."))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("role", "student")  # Ensure "role" is set
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault("role", "admin")  # Set default role for superusers

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(email, first_name, last_name, password, role="admin", **extra_fields)


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ('admin', _('Admin')),
        ('student', _('Student')),
        ('teacher', _('Teacher')),
    )

    email = models.EmailField(unique=True, verbose_name=_("Email"))
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="student", null=True, blank=True)
    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))

    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Is Staff"))
    is_superuser = models.BooleanField(default=False, verbose_name=_("Is Superuser"))
    last_login = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Login"))
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Registered At"))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def is_admin(self):
        return self.role == "admin"

    def is_teacher(self):
        return self.role == "teacher"

    def is_student(self):
        return self.role == "student"
