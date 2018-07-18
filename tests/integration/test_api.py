#!/usr/bin/env python
"""
    KiWi currency convertor homework.
    Author: Vladimir Svoboda
    Date created: 7/12/2018
"""

import pytest
import requests
import sys

from os.path import dirname, join, pardir
sys.path.append(join(dirname(__file__), pardir))

API_PORT = "8000"
API_HOST = "localhost"
API_PROTOCOL = "http"

API_URL = "{0}://{1}:{2}".format(API_PROTOCOL, API_HOST, API_PORT)

API_CURRENCY_CONVERTER = "currency_converter"
API_URL_CURRENCY_CONVERTER = "{0}/{1}".format(API_URL, API_CURRENCY_CONVERTER)

ROUND_PRECISION = 6
AMOUNT_MULTIPLIER = 10


def get_params(amount, input_currency, output_currency):
    return {
        'amount': amount,
        'input_currency': input_currency,
        'output_currency': output_currency
    }


def get_expected_result(amount,
                        input_currency,
                        output_currency,
                        output_currency_result):
    return \
        {
            "input": {
                "amount": amount,
                "currency": input_currency
            },
            "output": {
                output_currency: output_currency_result,
            }
        }


@pytest.mark.parametrize("amount,input_currency,output_currency", [
    (1.45, 'USD', 'CZK'),
    (10.99, 'CZK', 'EUR'),
    (100.11, 'EUR', 'USD'),
    (42, 'CNY', 'USD'),
    (18.45, 'GBP', 'CZK'),
])
def test_currency_converter_api(amount, input_currency, output_currency):
    r = requests.get(API_URL_CURRENCY_CONVERTER, params=get_params(amount,
                                                                   input_currency,
                                                                   output_currency))
    req_result = r.json()

    amount_of_input_curr = req_result['output'][output_currency]

    expected_result = get_expected_result(amount,
                                          input_currency,
                                          output_currency,
                                          amount_of_input_curr)

    assert expected_result == req_result

    r = requests.get(API_URL_CURRENCY_CONVERTER, params=get_params(AMOUNT_MULTIPLIER*amount,
                                                                   input_currency,
                                                                   output_currency))
    req_result = r.json()
    amount_of_input_curr_multiplied = req_result['output'][output_currency]

    assert round(amount_of_input_curr * AMOUNT_MULTIPLIER, ROUND_PRECISION) == round(amount_of_input_curr_multiplied, ROUND_PRECISION)


@pytest.mark.parametrize("amount,input_currency,through_currency,output_currency", [
    (10, 'USD', 'CZK', 'EUR'),
    (50, 'CNY', 'USD', 'EUR'),
    (20, 'GBP', 'CZK', 'EUR'),
])
def test_currency_converter_api(amount, input_currency, through_currency, output_currency):
    r = requests.get(API_URL_CURRENCY_CONVERTER, params=get_params(amount,
                                                                   input_currency,
                                                                   through_currency))
    req_result = r.json()

    conversion_to_through_curr = req_result['output'][through_currency]

    r = requests.get(API_URL_CURRENCY_CONVERTER, params=get_params(conversion_to_through_curr,
                                                                   through_currency,
                                                                   output_currency))
    req_result = r.json()
    conversion_through_to_output_curr = req_result['output'][output_currency]

    # Direct conversion into output cur.
    r = requests.get(API_URL_CURRENCY_CONVERTER, params=get_params(amount,
                                                                   input_currency,
                                                                   output_currency))
    direct_to_output_curr = req_result['output'][output_currency]

    assert round(direct_to_output_curr, ROUND_PRECISION) == round(
        conversion_through_to_output_curr, ROUND_PRECISION)
