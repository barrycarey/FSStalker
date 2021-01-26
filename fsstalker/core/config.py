import os
import sys
from configparser import ConfigParser
from typing import Text, NoReturn

from fsstalker.core.logging import log


class Config:

    def __init__(self, config_file: Text = None, **settings):
        self.loaded_config = None
        self._load_config(config_file=config_file)

    def _load_config(self, config_file=None) -> NoReturn:
        """
        Load the config file.

        Config file can either be passed in, pulled from the ENV, in CWD or in module dir.

        Load priority:
        1. Passed in config
        2. ENV
        3. CWD
        4 Module Dir
        :param config_file: path to config file
        :return: None
        """
        config_to_load = ()

        module_dir = os.path.dirname(sys.modules[__name__].__file__)
        log.debug('Checking for config in module dir: %s', module_dir)
        if os.path.isfile(os.path.join(module_dir, 'config.ini')):
            log.info('Found config.ini in module dir')
            config_to_load = os.path.join(module_dir, 'config.ini'), 'module'

        log.debug(f'Checking for config in current dir: %s', os.getcwd())
        if not config_to_load and os.path.isfile('sleuth_config.json'):
            log.info('Found config.ini in current directory')
            config_to_load = os.path.join(os.getcwd(), 'config.ini'), 'cwd'

        log.debug('Checking ENV for config file')
        if os.getenv('CONFIG', None):
            if os.path.isfile(os.getenv('CONFIG')):
                config_to_load = os.getenv('CONFIG'), 'env'
                log.info('Loading config provided in ENV: %s', config_to_load)

        if config_file:
            log.debug('Checking provided config file: %s', config_file)
            if os.path.isfile(config_file):
                config_to_load = config_file, 'passed'
            else:
                log.error('Provided config does not exist')

        if not config_to_load:
            log.error('Failed to locate config file')
            return

        log.info('Config Source: %s | Config File: %s', config_to_load[1], config_to_load[0])
        self.loaded_config = ConfigParser(config_to_load[0])