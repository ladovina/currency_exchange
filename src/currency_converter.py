#!/usr/bin/env python
"""
    KiWi currency convertor homework.
    Author: Vladimir Svoboda
    Date created: 7/12/2018
"""

import hug
import logging
import sys

from os.path import dirname, join, pardir
sys.path.append(join(dirname(__file__), pardir))

from config.options import Options
from src.converter import CurrencyConversionGenerator, CurrencyConvertor
from src.converter_exceptions import UnknownCurrencyException, NotUniqueInputCurrencyException

# create logger
logging.basicConfig(**Options['log'])
logger = logging.getLogger(__name__)

currency_conversion_generator = CurrencyConversionGenerator()


@hug.cli()
@hug.get(examples=["amount=150&input_currency=CZK&output_currency=USD",
                   "amount=10&input_currency=€&output_currency=$"])
def currency_converter(amount: hug.types.float_number=0,
                       input_currency: hug.types.text=None,
                       output_currency: hug.types.text=None):
    """
    Converts <amount> (float) of <input currency> (3 letters name or currency symbol)
    into <output currency> (3 letters name or currency symbol)
    """
    try:
        currency_conversion = currency_conversion_generator.\
            generate_conversion(amount, input_currency, output_currency)

        CurrencyConvertor().convert(currency_conversion)
    except (UnknownCurrencyException, NotUniqueInputCurrencyException) as e:
        logger.error(e)
        return {"error": "{}".format(e)}

    return currency_conversion.to_json()


if __name__ == '__main__':
    currency_converter.interface.cli()
