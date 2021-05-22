from django.db import models

class Asset(models.Model):
    symbol = models.TextField(primary_key=True)
    source = models.TextField()

    class Meta:
        managed = False
        db_table = 'asset'

class ExchangeRate(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    from_asset = models.ForeignKey(Asset, models.CASCADE, db_column='from_asset', related_name='rate_from_asset')
    to_asset = models.ForeignKey(Asset, models.CASCADE, db_column='to_asset', related_name='rate_to_asset')
    rate = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'exchange_rate'
        unique_together = (('timestamp', 'from_asset', 'to_asset'),)