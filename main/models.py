from django.db import models



class Reserve(models.Model):
    first_name = models.CharField(max_length=255 , verbose_name = "نام")
    last_name = models.CharField(max_length=255 , verbose_name = "نام خانوادگی")
    phone_number =  models.CharField(max_length=11 , verbose_name = "شماره تلفن")

    created_at = models.DateTimeField(auto_now_add=True , verbose_name = "تاریخ ساخت")
    update_at = models.DateTimeField(auto_now=True , verbose_name = "تاریخ اپدیت")

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
    
    def __str__(self):
        return f"رزرو {self.first_name}"
    
    class Meta :
        verbose_name = 'رزرو'
        verbose_name_plural= "رزروها"
        ordering = ("-created_at",)



