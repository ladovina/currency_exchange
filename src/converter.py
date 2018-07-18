#!/usr/bin/env python
"""
    KiWi currency convertor homework.
    Author: Vladimir Svoboda
    Date created: 7/12/2018
"""

from collections import defaultdict
import time
import logging

from config.options import Options
from forex_python.converter import CurrencyRates, CurrencyCodes
from src.converter_exceptions import UnknownCurrencyException, NotUniqueInputCurrencyException

# create logger
logging.basicConfig(**Options['log'])
logger = logging.getLogger(__name__)


class CurrencyConversion:
    """
    Class with all the information about the currency conversion.
    """

    def __init__(self, amount, input_currency, output_currencies, currency_rates):
        self.amount = amount
        self.input_currency = input_currency

        if not isinstance(output_currencies, list):
            raise TypeError("Variable output_currencies should be a list!")
        self.output_currencies = output_currencies

        self.currency_rates = currency_rates
        self.conversion_result = defaultdict(dict)
        self._init_empty_result()

    def _init_empty_result(self):
            for output_currency in self.output_currencies:
                self.conversion_result[self.input_currency][output_currency] = 0

    def to_json(self):
        json_data = {
            "input": {
                "amount": self.amount,
                "currency": self.input_currency
            },
            "output": {}
        }

        for output_currency in self.output_currencies:
            json_data["output"][output_currency] = \
                self.conversion_result[self.input_currency][output_currency]

        return json_data


class CurrencyConvertor:
    """
    Class which executes currency conversions.
    """

    @staticmethod
    def convert(conversion):
        logger.debug("Converting %f of %s to %s",
                     conversion.amount,
                     conversion.input_currency,
                     conversion.output_currencies)

        for output_currency in conversion.output_currencies:
            conversion.conversion_result[conversion.input_currency][output_currency] = \
                conversion.amount * conversion.currency_rates[output_currency]\
                / conversion.currency_rates[conversion.input_currency]

        logger.debug("Conversion done.")


class CurrencyConversionGenerator:
    # Currency used for request of all the available currencies.
    REQUEST_CURRENCY = 'USD'

    CURRENCY_RATES_THRESHOLD = 21600  # Update currency rates list every 6 hours.

    def __init__(self):
        self.currency_rates_last_update = time.time()
        self.currency_rates = self._get_all_currency_rates()
        self.currency_codes = CurrencyCodes()
        self.currency_shortcuts_to_symbols = {}
        self.request_currency_shortcuts_and_symbols()

        self.currency_symbols = [
            currency_symbol
            for currency_symbol in self.currency_shortcuts_to_symbols.values()
        ]

        self.currency_shortcuts = [
            currency_shortcut
            for currency_shortcut in self.currency_shortcuts_to_symbols.keys()
        ]

    def _get_all_currency_rates(self):
        self.currency_rates_last_update = time.time()
        currency_rates = CurrencyRates().get_rates(self.REQUEST_CURRENCY)

        # Add REQUEST_CURRENCY, since is missing, because we ask for rates for REQUEST_CURRENCY.
        currency_rates[self.REQUEST_CURRENCY] = 1

        return currency_rates

    def request_currency_shortcuts_and_symbols(self):
        for currency_shortcut, _ in self.currency_rates.items():
            currency_symbol = self.currency_codes.get_symbol(currency_shortcut)
            self.currency_shortcuts_to_symbols[currency_shortcut] = currency_symbol

        # Set symbol to '$', in all currencies, which contains '$'.
        for currency_shortcut, symbol in self.currency_shortcuts_to_symbols.items():
            if '$' in symbol:
                self.currency_shortcuts_to_symbols[currency_shortcut] = '$'

    def is_currency_symbol(self, currency):
        if currency in self.currency_symbols:
            return True

        return False

    def generate_conversion(self, amount, input_currency, output_currency):
        if self.should_update_currency_rates():
            self.update_currency_rates()

        input_currency_shortcuts = self.get_currencies_shortcut(input_currency)

        if len(input_currency_shortcuts) > 1:
            raise NotUniqueInputCurrencyException("Input currency symbol is not unique, "
                                                  "you should use currency shortcut instead "
                                                  "(USD, EUR, CZK etc.).")
        # Only one input currency allowed.
        input_currency_shortcut = input_currency_shortcuts[0]

        if output_currency:
            output_currency_shortcuts = self.get_currencies_shortcut(output_currency)

        else:
            # output_currency is None, we will convert intput currency to all available currencies.
            output_currency_shortcuts = self.currency_shortcuts

        return CurrencyConversion(amount, input_currency_shortcut,
                                  output_currency_shortcuts,
                                  self.currency_rates)

    def should_update_currency_rates(self):
        """
        We update currency rates only once per CURRENCY_RATES_THRESHOLD to speed up
        the conversion process.
        :return: None
        """
        if time.time() - self.currency_rates_last_update > self.CURRENCY_RATES_THRESHOLD:
            return True

        return False

    def update_currency_rates(self):
        self.currency_rates = self._get_all_currency_rates()

    def _get_shortcuts_from_symbol(self, currency_symbol):
        return [
                shortcut for shortcut, symbol in self.currency_shortcuts_to_symbols.items()
                if symbol == currency_symbol
            ]

    def _check_shortcut(self, currency_shortcut):
        # Convert all currency codes into upper so 'eur' is same like 'EUR'
        currency = currency_shortcut.upper()

        if currency in self.currency_shortcuts:
            return [currency]

        raise UnknownCurrencyException("Unknown currency {0}".format(currency))

    def get_currencies_shortcut(self, currency):
        """
        Method which returns currency shortcuts (USD, EUR etc.)
        for given currency symbol or returns existing shortcut, if currency is already shortcut.
        :param currency:
        :rtype: list
        :return: list of currency shortcuts, list because symbols like '$' are not unique.
        :raises UnknownCurrencyException when not known symbol/currency shortcut is supplied.
        """
        if self.is_currency_symbol(currency):
            return self._get_shortcuts_from_symbol(currency)

        return self._check_shortcut(currency)
