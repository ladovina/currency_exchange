#!/usr/bin/env bash

INT_TEST_DIR_NAME=$(dirname $0)
ROOT_PATH="${INT_TEST_DIR_NAME}/../.."
SRC_PATH="${ROOT_PATH}/src"

CONVERTER_API_SCRIPT="currency_converter.py"
TEST_API_SCRIPT="test_api.py"

# Activate venv
source ${ROOT_PATH}/venv/bin/activate

hug -f ${SRC_PATH}/${CONVERTER_API_SCRIPT} &
hug_server_pid=$!

sleep 2 # wait for server

pytest "${INT_TEST_DIR_NAME}/${TEST_API_SCRIPT}"

if [ $? -eq 0 ]; then
    echo "Integration tests OK!"
else
    echo "Integration tests FAILED!"
fi

kill -9 ${hug_server_pid}
