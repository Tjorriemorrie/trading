from django.db import models


class Snapshot(models.Model):
    snapped_at = models.DateField(unique=True)
    href = models.CharField(max_length=55)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cryptocurrency(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=20, unique=True)
    slug = models.CharField(max_length=50)
    added_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Quote(models.Model):
    snapshot = models.ForeignKey(
        Snapshot, on_delete=models.CASCADE, related_name='quotes')
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, on_delete=models.CASCADE, related_name='quotes')
    rank = models.IntegerField()

    max_supply = models.IntegerField(null=True)
    circulating_supply = models.IntegerField()
    total_supply = models.IntegerField()
    price = models.FloatField()
    volume_24h = models.FloatField()
    change_7d = models.FloatField()
    market_cap = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('snapshot', 'cryptocurrency', 'rank')
