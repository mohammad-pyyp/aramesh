

# class Appointment(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'در انتظار بررسی'),
#         ('confirmed', 'تایید شده'),
#         ('canceled', 'لغو شده'),
#     ]

#     TIME_CHOICES = [  
#         ('7'     ,   '7'      ) ,
#         ('7_30'  ,   '7:30'  ) ,
#         ('8'     ,   '8'      ) ,
#         ('8_30'  ,   '8:30'  ) ,
#         ('9'     ,   '9'      ) ,
#         ('9_30'  ,   '9:30'  ) ,
#         ('10'    ,   '10'     ) ,
#         ('10_30' ,   '10:30'  ) ,
#         ('11'    ,   '11'     ) ,

#     ]
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
#     date = models.DateField(null=True, blank=True )
#     time = models.CharField(null=True, blank=True )
#     # profile = models.ForeignKey(Profile , on_delete=models.CASCADE , null=True , blank=True)

    
#     def __str__(self):
#         return f"رزرو {self.profile_first_name}"
    
#     class Meta :
#         verbose_name = 'رزرو'
#         verbose_name_plural= "رزروها"
#         # ordering = ("-created_at",)

#     def __str__(self):
#         return f"{self.profile_fullname} - {self.date} {self.time}"


