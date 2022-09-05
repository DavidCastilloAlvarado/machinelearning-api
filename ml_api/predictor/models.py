from django.db import models

# Create your models here.


class ModelSink(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)
    name = models.CharField(max_length=500, null=False)
    description = models.TextField()
    version = models.CharField(max_length=500, )
    url = models.URLField(max_length=1000, )

    class Meta:
        db_table = 'model_sink'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'version'], name='models_sink_pk')
        ]
        indexes = [
            models.Index(fields=['name', 'version']),
        ]

    def __str__(self):
        return self.name
