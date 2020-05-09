import configparser
from typing import List

import ofxtools.config


def convert_list(string: str) -> List[str]:
    """
    Deserialize INI representation to a Python list
    """
    return [sub.strip() for sub in string.split(",")]


class UserConfig(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        kwargs["converters"] = {"list": convert_list}
        super().__init__(*args, **kwargs)


def get_user_cfg():
    user_cfg = UserConfig()
    ofx_config_file = ofxtools.config.USERCONFIGDIR / 'ofxget.cfg'
    user_cfg.read(ofx_config_file)
    return user_cfg


def setup():
    pass


if __name__ == '__main__':
    pass
