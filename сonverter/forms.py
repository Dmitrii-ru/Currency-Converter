
from django import forms
from .models import ExchangeRatesModel, CurrencyAccountsModel
from django.core.exceptions import ValidationError
from users.models import Profile
from decimal import *
from django.contrib import messages


class RatesForm(forms.Form):
    user = None
    input_5=Decimal
    change = ExchangeRatesModel.objects.all()
    input_sum = forms.DecimalField(required=True,label=False, widget=forms.TextInput(attrs={ 'placeholder': 'Введите сумму'}))
    what_we_exchange = forms.ModelChoiceField(change,empty_label='Что продаем',label=False)
    what_do_we_want_to_change = forms.ModelChoiceField(change ,empty_label="Что покупаем",label=False)



    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(RatesForm, self).__init__(*args, **kwargs)

    def clean_input_sum(self):
        input_sum = self.cleaned_data['input_sum']
        self.input_5 = self.cleaned_data['input_sum']
        if input_sum < 0:
            raise ValidationError('Сумма должна быть положительной')
        return input_sum

    def clean_what_we_exchange(self):

        what_we_exchange = self.cleaned_data['what_we_exchange']
# комиссия 5 процентов
        input_sum_5= self.input_5 / 100 * 5 +self.input_5
        if self.user:
            CAM = CurrencyAccountsModel.objects.filter(userID=self.user, currencies=what_we_exchange)
            if not CAM:
                raise ValidationError(f'Купите {what_we_exchange}')
            elif CAM.first().currency_account < input_sum_5:
                raise ValidationError(f'Не достаточно  {what_we_exchange}, не хватает {round(input_sum_5-CAM.first().currency_account,2)} комиссия 5 %' )
        return what_we_exchange
