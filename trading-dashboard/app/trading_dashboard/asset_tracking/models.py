from django.db import models

class Asset(models.Model):
    asset_symbol = models.TextField(primary_key=True)
    source = models.TextField()

    class Meta:
        managed = False
        db_table = 'asset'