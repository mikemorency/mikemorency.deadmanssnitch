#!/bin/sh

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
prefix=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 6)

touch "$SCRIPT_DIR/integration_config.yml"
: > "$SCRIPT_DIR/integration_config.yml"
{
    echo "---"
    echo "integration_config_dms_api_key: '$DMS_API_KEY'"
    echo "test_prefix: 'ansible-test-$prefix'"
} >> "$SCRIPT_DIR/integration_config.yml"
