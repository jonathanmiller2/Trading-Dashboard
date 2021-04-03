from django.db import models

class Ticker(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    symbol = models.TextField()
    val = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ticker'
        unique_together = (('timestamp', 'symbol'),)