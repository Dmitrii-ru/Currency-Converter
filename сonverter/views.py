from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from datetime import datetime
from .forms import RatesForm
from .models import ExchangeRatesModel, ExchangeHistery, CurrencyAccountsModel
from decimal import *
import time
from django.contrib import messages
from threading import Timer


# Вычитаем из что меняем сумму инпута и прибавляем на что меняем
def updateCA(request, what_do_we_want_to_change_s, converted_amost, what_we_exchange_s, input_sum):
    currency_account = CurrencyAccountsModel.objects.filter(userID=request.user,
                                                            currencies=what_do_we_want_to_change_s.currencies).exists()
    what_we_exchange_CA = CurrencyAccountsModel.objects.get(userID=request.user,
                                                            currencies=what_we_exchange_s.currencies)
    what_we_exchange_CA.currency_account = round(what_we_exchange_CA.currency_account - Decimal(input_sum / 100 * 5 + input_sum), 2)
    what_we_exchange_CA.save()
    if currency_account:
        update_CA = CurrencyAccountsModel.objects.get(userID=request.user,
                                                      currencies=what_do_we_want_to_change_s.currencies)
        update_CA.currency_account = round(update_CA.currency_account + converted_amost, 2)
        update_CA.save()
    else:
        CurrencyAccountsModel(userID=request.user,
                              currencies=what_do_we_want_to_change_s.currencies,
                              currency_account=converted_amost).save()

# Если user auth, обмен валюты, обновление данных в бд, запись истории обмена
def User_authenticated(request):
    format1 = '%d.%m.%Y - %H:%M:%S'
    list_CAM = CurrencyAccountsModel.objects.filter(userID=request.user)
    form = RatesForm(request.POST, user=request.user)
    store5 = ExchangeHistery.objects.filter(userID=request.user).order_by('-data')[:5]
    if request.method == 'POST' and form.is_valid():
        input_sum = Decimal(form.data.get('input_sum'))
        what_we_exchange_s = ExchangeRatesModel.objects.get(pk=form.data.get('what_we_exchange'))
        what_do_we_want_to_change_s = ExchangeRatesModel.objects.get(pk=form.data.get('what_do_we_want_to_change'))
        converted_amost = Decimal(round(
            (what_do_we_want_to_change_s.exchange / what_we_exchange_s.exchange) * input_sum, 2))
        if request.user.is_authenticated:
            try:
                ExchangeHistery(userID=request.user, data=datetime.strftime(datetime.now(), format1),
                                story=f'{input_sum / 100 * 5 + input_sum} {what_we_exchange_s.currencies}  обменяли на  {converted_amost} {what_do_we_want_to_change_s.currencies}').save()
                updateCA(request, what_do_we_want_to_change_s, converted_amost, what_we_exchange_s, input_sum)
                form = RatesForm()
                return render(request, 'converter/index.html', {'form': form, 'store5': store5, 'list_CAM': list_CAM})
            except:
                messages.success(request, f'Произошел сбой')
                return render(request, 'converter/index.html', {'form': form, 'store5': store5, 'list_CAM': list_CAM})
        else:
            store1 = f'{input_sum}  {what_we_exchange_s.currencies} обменяли на {what_do_we_want_to_change_s.currencies}  Итого: {converted_amost} {what_do_we_want_to_change_s.currencies}  '
            return render(request, 'converter/index.html', {'form': form, 'store5': store1})
    return render(request, 'converter/index.html', {'form': form, 'list_CAM': list_CAM, 'store5': store5})

# Если не user auth,
def User_not_authenticated(request):
    form = RatesForm()
    if request.method == 'POST':
        form = RatesForm(request.POST)
        if form.is_valid():
            input_sum = form.data.get('input_sum')
            what_we_exchange_s = ExchangeRatesModel.objects.get(pk=form.data.get('what_we_exchange'))
            what_do_we_want_to_change_s = ExchangeRatesModel.objects.get(pk=form.data.get('what_do_we_want_to_change'))
            converted_amost = Decimal(round(
                (what_we_exchange_s.exchange / what_do_we_want_to_change_s.exchange) * Decimal(input_sum), 10))
            store1 = f'{input_sum}  {what_we_exchange_s.currencies} обменяли на {what_do_we_want_to_change_s.currencies}  Итого: {converted_amost} {what_do_we_want_to_change_s.currencies}  '
            return render(request, 'converter/index.html', {'form': form, 'store5': store1})
    return render(request, 'converter/index.html', {'form': form})


def exchenge(request):
    if request.user.is_authenticated:
        return User_authenticated(request)
    else:
        return User_not_authenticated(request)

# Добавить 100 баксов User
def fill_up_a_purse(request):
    format1 = '%d.%m.%Y - %H:%M:%S'
    if request.user.is_authenticated:
        upcurrAccounts = CurrencyAccountsModel.objects.get(userID=request.user,
                                                           currencies='USD')
        upcurrAccounts.currency_account = upcurrAccounts.currency_account + Decimal(100)
        upcurrAccounts.save()
        ExchangeHistery(userID=request.user,
                        data=datetime.strftime(datetime.now(), format1),
                        story=f'Пополнение счета на 100 USD').save()

    return redirect('index')

# Обновление бд курсов валют
def upcurrdefauto(request):

    response = requests.get(url='https://www.cbr-xml-daily.ru/latest.js').json()
    curr = response.get('rates')
    Timer(2000, upcurrdefauto).start()
    for k, v in curr.items():
        if ExchangeRatesModel.objects.filter(currencies=k).only('currencies'):
            old_curr = ExchangeRatesModel.objects.get(currencies=k)
            old_curr.exchange = float(v)
            old_curr.save()
        else:
            ExchangeRatesModel(currencies=k, exchange=float(v)).save()
    messages.success(request, f'Загрузка валют завершена ')
    return redirect('index')
