from django.db import models

class Asset(models.Model):
    symbol = models.TextField(primary_key=True)
    source = models.TextField()

    class Meta:
        managed = False
        db_table = 'asset'