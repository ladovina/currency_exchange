#!/usr/bin/env python
"""
    KiWi currency convertor homework.
    Author: Vladimir Svoboda
    Date created: 7/12/2018
"""

import time
import pytest
import sys

from os.path import dirname, join, pardir
sys.path.append(join(dirname(__file__), pardir))

from src.converter import CurrencyConversion, CurrencyConvertor
from src.converter import CurrencyConversionGenerator
from src.converter_exceptions import NotUniqueInputCurrencyException

TEST_CURRENCY_RATES = {'CZK': 22.0, 'EUR': 0.8, 'USD': 1}


def test_currency_conversion():
    currency_rates = TEST_CURRENCY_RATES
    conversion = CurrencyConversion(10, 'USD', ['EUR'], currency_rates)

    assert conversion.amount == 10
    assert conversion.input_currency == 'USD'
    assert conversion.output_currencies == ['EUR']
    assert conversion.currency_rates == currency_rates

    with pytest.raises(TypeError):
        CurrencyConversion(10, 'USD', 'EUR', currency_rates)


@pytest.mark.parametrize("currency_symbol,expected_currency_shortcut", [
    ('BGN', 'BGN'),
    ('Fr.', 'CHF'),
    ('Kč', 'CZK'),
    ('€', 'EUR'),
    ('£', 'GBP'),
    ('kn', 'HRK'),
    ('Ft', 'HUF'),
    ('Rp', 'IDR'),
    ('₪', 'ILS'),
    ('₹', 'INR'),
    ('W', 'KRW'),
    ('RM', 'MYR'),
    ('₱', 'PHP'),
    ('zł', 'PLN'),
    ('L', 'RON'),
    ('฿', 'THB'),
    ('TRY', 'TRY'),
])
def test_currency_conversion_generator_unique(currency_symbol,
                                       expected_currency_shortcut):
    currency_generator = CurrencyConversionGenerator()
    conversion = currency_generator.generate_conversion(100, currency_symbol, None)
    assert conversion.input_currency == expected_currency_shortcut


@pytest.mark.parametrize("currency_symbol,expected_currency_shortcut", [
    ('$', 'AUD'),
    ('kr', 'SEK'),
    ('R', 'RUB'),
    ('¥', 'JPY'),
])
def test_currency_conversion_generator_not_unique(currency_symbol, expected_currency_shortcut):
    currency_generator = CurrencyConversionGenerator()
    with pytest.raises(NotUniqueInputCurrencyException):
        currency_generator.generate_conversion(100, currency_symbol, None)


def test_should_update_currency_rates():
    conversion_generator = CurrencyConversionGenerator()
    conversion_generator.currency_rates = None

    assert not conversion_generator.should_update_currency_rates()

    conversion_generator.currency_rates_last_update = \
        time.time() - conversion_generator.CURRENCY_RATES_THRESHOLD - 1

    assert conversion_generator.should_update_currency_rates()


def test_update_currency_rates():
    conversion_generator = CurrencyConversionGenerator()
    conversion_generator.currency_rates = None

    generated_conversion = conversion_generator.\
        generate_conversion(0, 'CZK', 'USD')

    assert not generated_conversion.currency_rates

    # Currency rates should be updated now
    conversion_generator.currency_rates_last_update = \
        time.time() - conversion_generator.CURRENCY_RATES_THRESHOLD - 1

    generated_conversion = conversion_generator. \
        generate_conversion(0, 'CZK', 'USD')

    assert generated_conversion.currency_rates


def test_generate_conversion():
    conversion_generator = CurrencyConversionGenerator()
    conversion_generator.currency_rates = TEST_CURRENCY_RATES

    conversion = conversion_generator.generate_conversion(TEST_CURRENCY_RATES['CZK'], 'CZK', 'USD')
    CurrencyConvertor.convert(conversion)
    assert conversion.conversion_result['CZK']['USD'] == 1

    usd_amount = 100
    conversion = conversion_generator.generate_conversion(usd_amount, "USD", 'CZK')
    CurrencyConvertor.convert(conversion)
    assert len(conversion.output_currencies) == 1
    assert conversion.conversion_result['USD']['CZK'] == \
           usd_amount * TEST_CURRENCY_RATES['CZK']

    conversion_generator = CurrencyConversionGenerator()
    conversion = conversion_generator.generate_conversion(TEST_CURRENCY_RATES['CZK'], 'CZK', None)
    CurrencyConvertor.convert(conversion)
    assert len(conversion.conversion_result['CZK']) == \
           len(conversion_generator.currency_shortcuts)

    conversion = conversion_generator.generate_conversion(0, "USD", "CZK")
    CurrencyConvertor.convert(conversion)
    assert conversion.conversion_result['USD']['CZK'] == 0
    assert len(conversion.conversion_result['USD']) == 1


@pytest.mark.parametrize("value,is_currency_symbol_expected", [
    ('BGN', True),
    ('BGN', True),
    ('Fr.', True),
    ('CHF', False),
    ('Kč', True),
    ('CZK', False),
    ('€', True),
    ('EUR', False),
    ('£', True),
    ('GBP', False),
    ('kn', True),
    ('HRK', False),
    ('Ft', True),
    ('HUF', False),
    ('Rp', True),
    ('IDR', False),
    ('₪', True),
    ('ILS', False),
    ('₹', True),
    ('INR', False),
    ('W', True),
    ('KRW', False),
    ('RM', True),
    ('MYR', False),
    ('₱', True),
    ('PHP', False),
    ('zł', True),
    ('PLN', False),
    ('L', True),
    ('RON', False),
    ('฿', True),
    ('THB', False),
    ('TRY', True),
    ('TRY', True),
    ('$', True),
    ('AUD', False),
    ('kr', True),
    ('SEK', False),
    ('R', True),
    ('RUB', False),
    ('¥', True),
    ('JPY', False),
])
def test_is_currency_symbol(value, is_currency_symbol_expected):
    conversion_generator = CurrencyConversionGenerator()
    is_currency_symbol_result = conversion_generator.is_currency_symbol(value)

    assert is_currency_symbol_result == is_currency_symbol_expected
