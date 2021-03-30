from django.db import models

class Ticker_GME(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    val = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ticker_gme'