from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class ExchangeHistery(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    data = models.CharField(max_length=20)
    story = models.CharField(max_length=100)


class ExchangeRatesModel(models.Model):
    currencies = models.CharField(null=True, max_length=10)
    exchange = models.DecimalField(null=True, max_digits=10000000000, decimal_places=10)

    def __str__(self):
        return f'{self.currencies}'


class CurrencyAccountsModel(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    currencies = models.CharField(null=True, max_length=10)
    currency_account = models.DecimalField(null=True, max_digits=10000000000, decimal_places=2)

