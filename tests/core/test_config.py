import os
from configparser import ConfigParser
from unittest import TestCase

from fsstalker.core.config import Config


class TestConfig(TestCase):

    def test__fetch_config_value_return_lower_section_ini_value(self):
        config = Config()
        self.assertEqual('test_db_user', config._fetch_config_value('username', 'database'))

    def test__fetch_config_value_return_upper_section_ini_value(self):
        config = Config()
        self.assertEqual('test_db_user', config._fetch_config_value('username', 'DATABASE'))

    def test__fetch_config_value_bad_section_return_none(self):
        config = Config()
        self.assertIsNone(config._fetch_config_value('username', 'DUMMY'))

    def test__fetch_config_value_return_env_value(self):
        config = Config()
        os.environ['database_username'] = 'env_user'
        self.assertEqual('env_user', config._fetch_config_value('username', 'DATABASE'))
        del os.environ['database_username']

    def test__fetch_config_value_return_custom(self):
        config = Config(database_username='passed_user')
        self.assertEqual('passed_user', config._fetch_config_value('username', 'DATABASE'))

    def test_redis_url_with_password(self):
        config = Config()
        config.loaded_config['REDIS']['password'] = 'testpass'
        self.assertEqual('redis://user:testpass@localhost:6379/0', config.redis_url)

    def test_redis_url_without_password(self):
        config = Config()
        self.assertEqual('redis://localhost:6379/0', config.redis_url)

    def get_config(self) -> ConfigParser:
        config = ConfigParser()
        config['DATABASE'] = {'name': 'test', 'hostname': 'test.com', 'port': 3306, 'username': 'test_user', 'password': 'test_password'}
        config['REDDIT'] = {'client_id': 'abc123', 'client_secret': '123abc', 'useragent': 'test agent', 'username': 'test_user', 'password': 'test_password'}
        config['LOGGING'] = {'level': 'info'}
        config['REDIS'] = {'host': 'localhost', 'port': 2379, 'database': 0, 'password': 'testpass'}