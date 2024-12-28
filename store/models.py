# Django imports
from django.db import models


class ContactMessage(models.Model):
    '''
    Model to store contact messages submitted by users.

    Attributes:
        STATUS_CHOICES (list): Predefined status options for messages.
        status (str): Current status of the message.
        subject (str): Subject of the message.
        email (str): Email address of the sender.
        name (str): Name of the sender.
        message (str): Content of the message.
        created_at (datetime): Timestamp when the message was created.
    '''
    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('replied', 'Replied'),
        ('spam', 'Spam'),
    ]

    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default='new',
        blank=False, null=False
    )
    subject = models.CharField(max_length=100)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''
        Return a string representation of the contact message.

        Returns:
            str: Concatenation of sender name and message subject.
        '''
        return f"{self.name} - {self.subject}"
