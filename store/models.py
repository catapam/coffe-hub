from django.db import models

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('replied', 'Replied'),
        ('spam', 'Spam'),
    ]
    
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='new', blank=False, null=False)
    subject = models.CharField(max_length=100)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
