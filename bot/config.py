from collections import defaultdict
from typing import Any

from ruamel.yaml import YAML

yaml = YAML()
config = yaml.load(open("config.yaml"))


class ConfigItem(defaultdict):
    def __init__(self, data):
        super(ConfigItem, self).__init__(ConfigItem)
        for k, v in data.items():
            self[k] = v

    def __getattr__(self, item):
        try:
            return self[item]
        except AttributeError:
            return None

    def __setattr__(self, key, value):
        self[key] = value


class Config(defaultdict):
    def __init__(self, data=config):
        super(Config, self).__init__(Config)
        for k, v in data.items():
            self[k] = ConfigItem(dict(v))

    def __getattr__(self, item):
        try:
            return self[item]
        except AttributeError:
            return None

    def __setattr__(self, key, value):
        self[key] = value
