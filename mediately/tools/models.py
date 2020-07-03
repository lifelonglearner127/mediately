from django.contrib.postgres.fields import JSONField
from django.db import models


class Tool(models.Model):
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=2)
    json_spec = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ['name', 'language']

    def __str__(self):
        return f'{self.name} - {self.language}'
