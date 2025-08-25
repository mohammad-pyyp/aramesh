from django.db import models
from django.core.validators import RegexValidator


class Profile(models.Model):
    first_name = models.CharField(max_length=255, verbose_name='نام')
    last_name = models.CharField(max_length=255, verbose_name='نام خانوادگی')
    phone_number = models.CharField(max_length=11, unique=True , validators=[RegexValidator(regex='^09\d{9}$',
                                    message='شماره تلفن باید با 09 شروع شده و 11 رقم باشد')], verbose_name='شماره تلفن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    @property
    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def abjad(self):
        abjad_dict = {
            'ا': 1, 'ب': 2, 'ج': 3, 'د': 4,
            'ه': 5, 'و': 6, 'ز': 7, 'ح': 8,
            'ط': 9, 'ی': 10, 'ك': 20, 'ک': 20,
            'ل': 30, 'م': 40, 'ن': 50, 'س': 60,
            'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100,
            'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500,
            'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900,
            'غ': 1000
        }

        total = 0
        for char in self.first_name:
            if char in abjad_dict:
                total += abjad_dict[char]
        
        return total

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'

    def __str__(self):
        return f"پروفایل {self.get_fullname()}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('confirmed', 'تایید شده'),
        ('cancel', 'لغو شده'),
    ]

    TIME_CHOICES = [  
        ('7'     ,   '7'      ) ,
        ('7_30'  ,   '7:30'  ) ,
        ('8'     ,   '8'      ) ,
        ('8_30'  ,   '8:30'  ) ,
        ('9'     ,   '9'      ) ,
        ('9_30'  ,   '9:30'  ) ,
        ('10'    ,   '10'     ) ,
        ('10_30' ,   '10:30'  ) ,
        ('11'    ,   '11'     ) ,

    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    date = models.DateField(null=True, blank=True )
    time = models.CharField(null=True, blank=True )
    profile = models.ForeignKey(Profile , on_delete=models.CASCADE , null=True , blank=True)

    
    def __str__(self):
        return f"رزرو {self.profile_first_name}"
    
    class Meta :
        verbose_name = 'رزرو'
        verbose_name_plural= "رزروها"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.profile_fullname} - {self.date} {self.time}"
