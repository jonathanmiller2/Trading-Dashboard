from django.db import models

class Algo(models.Model):
    algo_id = models.IntegerField(primary_key=True)
    algo_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'algo'


class Asset(models.Model):
    asset_symbol = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'asset'

class Balance(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    algo = models.ForeignKey(Algo, models.DO_NOTHING)
    asset_symbol = models.ForeignKey(Asset, models.DO_NOTHING, db_column='asset_symbol')
    balance = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'balance'
        unique_together = (('timestamp', 'algo', 'asset_symbol'),)

class ExchangeRate(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    from_asset = models.ForeignKey(Asset, models.DO_NOTHING, db_column='from_asset')
    to_asset = models.ForeignKey(Asset, models.DO_NOTHING, db_column='to_asset')
    rate = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'exchange_rate'
        unique_together = (('timestamp', 'from_asset', 'to_asset'),)


class Trade(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    algo = models.ForeignKey(Algo, models.DO_NOTHING)
    from_asset = models.ForeignKey(Asset, models.DO_NOTHING, db_column='from_asset')
    to_asset = models.ForeignKey(Asset, models.DO_NOTHING, db_column='to_asset')
    amount = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'trade'
        unique_together = (('timestamp', 'algo', 'from_asset', 'to_asset'),)