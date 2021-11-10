"""
    This file s used to load environment variables from a powershell file
"""

import os
from typing import Optional


def get_env(filename: str) -> Optional[dict]:
    """
        This function is used to get environment variables from a powershell file as a dictionary

        :param filename: The file to read
        :type filename: str
        :returns: The environment variables in the file as a dictionary
        :rtype: dict
    """

    env = {}
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for raw_line in file.readlines():
                if raw_line[0] != "#":
                    line = raw_line[5:].split('=')
                    env[line[0]] = line[1].replace('"', "")[:-1]
        return env
    else:
        return None


def load_to_env(filename: str) -> None:
    """
        This function is used to load a powershell file into the environment

        :param filename: The name/path of the powershell file to load
        :type filename: str
    """

    env = get_env(filename)
    if env is not None:
        for key in env.keys():
            os.environ[key] = env[key]
