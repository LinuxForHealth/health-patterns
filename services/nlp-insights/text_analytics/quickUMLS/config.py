import os
import configparser

# if the following is an environment variable on the system, the service will pull config from the corresponding file,
# otherwise default to the source config
QUICKUMLS_CONFIG_ENVVAR = 'WHPA_CDP_UMLS_CONFIG'

quickumls_header = 'QUICKUMLS_CONFIG'
quickumls_required_keys = ['QUICKUMLS_URL']

_quickumls_configs = None


def _load_configs():
    global _quickumls_configs

    quickumls_config_file_path = os.getenv(QUICKUMLS_CONFIG_ENVVAR, 'text_analytics/quickUMLS/quickumls_config.ini')
    configParser = configparser.ConfigParser()
    configParser.read(quickumls_config_file_path)
    _quickumls_configs = configParser[quickumls_header]


def get_config():
    if _quickumls_configs is None:
        _load_configs()
    return _quickumls_configs
