import os
import sys
from configparser import ConfigParser
from typing import Text, NoReturn, Optional

from fsstalker.core.logging import log


class Config:

    def __init__(self, config_file: Text = None, **custom):
        self.loaded_config = ConfigParser()
        self._load_config(config_file=config_file)
        self._custom = custom

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
        if not config_to_load and os.path.isfile('config.ini'):
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
        self.loaded_config.read(config_to_load[0])

    def _fetch_config_value(self, key, section) -> Optional[Text]:
        """
        Take a key and section and attempt to load the config
        :rtype: Text
        :param key:
        :param section:
        """
        section = section.upper()
        combined_key = f'{section.lower()}_{key}'
        env_value = os.getenv(combined_key, default=None)
        custom_value = self._custom.get(combined_key)
        ini_value = None
        if self.loaded_config.has_section(section):
            ini_value = self.loaded_config[section].get(key)

        return env_value or custom_value or ini_value

    @property
    def database_user(self):
        return self._fetch_config_value('username', 'database')

    @property
    def database_password(self):
        return self._fetch_config_value('password', 'database')

    @property
    def database_name(self):
        return self._fetch_config_value('name', 'database')

    @property
    def database_hostname(self):
        return self._fetch_config_value('hostname', 'database')

    @property
    def database_port(self):
        port = self._fetch_config_value('port', 'database')
        try:
            port = int(port)
        except TypeError:
            pass
        return port

    @property
    def reddit_client_id(self):
        return self._fetch_config_value('client_id', 'reddit')

    @property
    def reddit_client_secret(self):
        return self._fetch_config_value('client_secret', 'reddit')

    @property
    def reddit_client_secret(self):
        return self._fetch_config_value('client_secret', 'reddit')

    @property
    def reddit_useragent(self):
        return self._fetch_config_value('useragent', 'reddit')

    @property
    def reddit_username(self):
        return self._fetch_config_value('username', 'reddit')

    @property
    def reddit_password(self):
        return self._fetch_config_value('password', 'reddit')

    @property
    def redis_url(self):
        if not self.redis_password:
            return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_database}'
        return f'redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_database}'

    @property
    def redis_host(self):
        return self._fetch_config_value('host', 'redis')

    @property
    def redis_port(self):
        return self._fetch_config_value('port', 'redis')

    @property
    def redis_database(self):
        return self._fetch_config_value('database', 'redis')

    @property
    def redis_password(self):
        return self._fetch_config_value('password', 'redis')

    @property
    def patreon_client_id(self):
        return self._fetch_config_value('client_id', 'patreon')

    @property
    def patreon_client_secret(self):
        return self._fetch_config_value('client_secret', 'patreon')

    @property
    def patreon_redirect_uri(self):
        return self._fetch_config_value('redirect_uri', 'patreon')

    @property
    def patreon_auth_token(self):
        return self._fetch_config_value('auth_token', 'patreon')