from django.db import models


class Day(models.Model):
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.title



