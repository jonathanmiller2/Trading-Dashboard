from django.db import models
from trading_dashboard.asset_tracking.models import Asset

class Algo(models.Model):
    algo_id = models.IntegerField(primary_key=True)
    algo_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'algo'

class Balance(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    algo = models.ForeignKey(Algo, models.CASCADE)
    asset_symbol = models.ForeignKey(Asset, models.CASCADE, db_column='asset_symbol')
    balance = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'balance'
        unique_together = (('timestamp', 'algo', 'asset_symbol'),)

class ExchangeRate(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    from_asset = models.ForeignKey(Asset, models.CASCADE, db_column='from_asset', related_name="ers_from_asset")
    to_asset = models.ForeignKey(Asset, models.CASCADE, db_column='to_asset', related_name="ers_to_asset")
    rate = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'exchange_rate'
        unique_together = (('timestamp', 'from_asset', 'to_asset'),)

class Trade(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    algo = models.ForeignKey(Algo, models.CASCADE)
    from_asset = models.ForeignKey(Asset, models.CASCADE, db_column='from_asset', related_name="trades_from_asset")
    to_asset = models.ForeignKey(Asset, models.CASCADE, db_column='to_asset', related_name="trades_to_asset")
    amount = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'trade'
        unique_together = (('timestamp', 'algo', 'from_asset', 'to_asset'),)