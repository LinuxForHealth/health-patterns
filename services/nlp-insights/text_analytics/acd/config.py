import os
import configparser

# if the following is an environment variable on the system, the service will pull config from the corresponding file,
# otherwise default to the source config
ACD_CONFIG_ENVVAR = 'ACD_CONFIG'

acd_header = 'ACD_CONFIG'
acd_required_keys = ['ACD_KEY', 'ACD_URL', 'ACD_FLOW']

_acd_configs = None


def _load_configs():
    global _acd_configs

    acd_config_file_path = os.getenv(ACD_CONFIG_ENVVAR, 'text_analytics/acd/acd_config.ini')
    configParser = configparser.ConfigParser()
    configParser.read(acd_config_file_path)
    _acd_configs = configParser[acd_header]

def get_config():
    if _acd_configs is None:
        _load_configs()
    return _acd_configs
