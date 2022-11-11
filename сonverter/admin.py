from django.contrib import admin
from .models import ExchangeRatesModel, ExchangeHistery, CurrencyAccountsModel

admin.site.register(ExchangeRatesModel)
admin.site.register(ExchangeHistery)
admin.site.register(CurrencyAccountsModel)

# Register your models here.
