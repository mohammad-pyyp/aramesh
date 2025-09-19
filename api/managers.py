from django.contrib.auth.base_user import BaseUserManager

# ---------- User ----------
class UserManager(BaseUserManager):
    def create_user(self, phone, first_name, last_name, password=None, **extra_fields):
        if not phone:
            raise ValueError('کاربر باید شماره تلفن داشته باشد')
        if not first_name or not last_name:
            raise ValueError('نام و نام خانوادگی ضروری است')

        user = self.model(phone=phone, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # برای سوپریوزر، نام و نام خانوادگی را به صورت پیش‌فرض تنظیم می‌کنیم
        extra_fields.setdefault('first_name', 'ادمین')
        extra_fields.setdefault('last_name', 'سیستم')
        
        return self.create_user(phone=phone, password=password, **extra_fields)