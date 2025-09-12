from django.contrib.auth.base_user import BaseUserManager

# ---------- User ----------
class UserManager(BaseUserManager):
    def create_user(self, phone, first_name='', last_name='', password=None, **extra_fields):
        if not phone:
            raise ValueError('Users must have a phone number')
        phone = phone.strip()
        user = self.model(phone=phone, first_name=first_name, last_name=last_name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if password is None:
            raise ValueError('Superuser must have a password.')
        return self.create_user(phone=phone, password=password, **extra_fields)

