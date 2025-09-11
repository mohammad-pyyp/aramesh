from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در حال بررسی'),
        ('approved', 'تایید شد'),
        ('canceled', 'لغو شد'),
    ]
    
    SERVICE_CHOICES = [
        ('مشاوره', 'مشاوره'),
        ('معاینه', 'معاینه'),
        ('درمان', 'درمان'),
        ('پیگیری', 'پیگیری'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmed_date = models.DateField(blank=True, null=True)
    confirmed_time = models.TimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.service} - {self.status}"

# Create your models here.
