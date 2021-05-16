from django.db import models
from trading_dashboard.asset_tracking.models import Asset

class Algo(models.Model):
    name = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'algo'

class Balance(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    algo = models.ForeignKey(Algo, models.CASCADE, db_column='algo')
    asset = models.ForeignKey(Asset, models.CASCADE, db_column='asset')
    
    balance = models.DecimalField(max_digits=500, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'balance'
        unique_together = (('timestamp', 'algo', 'asset'),)

class TradesOn(models.Model):
    algo = models.ForeignKey(Algo, models.CASCADE, db_column='algo', primary_key=True)
    asset = models.ForeignKey(Asset, models.CASCADE, db_column='asset')

    class Meta:
        managed = False
        db_table = 'trades_on'
        unique_together = (('algo', 'asset'),)