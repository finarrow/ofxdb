"""OFX account module.

Contains methods used to retrieve account details from the ofxtools generated ofxget.cfg file.
"""
from typing import List
from configparser import ConfigParser

from ofxdb import cfg

# -----------------------------------------------------------------------------
# -- User config parsing class
# -----------------------------------------------------------------------------


def convert_list(string: str) -> List[str]:
    """Convert INI list representation to a Python list."""
    return [sub.strip() for sub in string.split(",")]


class UserConfig(ConfigParser):
    """User config class. Extends ConfigParser with converter for INI list representation."""
    def __init__(self, *args, **kwargs):
        kwargs["converters"] = {"list": convert_list}
        super().__init__(*args, **kwargs)


# -----------------------------------------------------------------------------
# -- User config parsing method
# -----------------------------------------------------------------------------


def get_user_cfg() -> UserConfig:
    """Retrieve user config from ofxget.cfg file."""
    user_cfg = UserConfig()
    user_cfg.read(cfg.OFXGET_CFG)
    return user_cfg


if __name__ == '__main__':
    pass
