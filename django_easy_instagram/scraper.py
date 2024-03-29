"""
Created on 04/sep/2016

@author: Marco Pompili
"""

import html5lib as html
import json
import logging
import requests

from socket import error as socket_error
from requests.exceptions import ConnectionError, HTTPError

from . import settings

SCRIPT_JSON_PREFIX = 18
SCRIPT_JSON_DATA_INDEX = 21


def instagram_scrape_profile(username):
    """
    Scrap an instagram profile page
    :param username:
    :return:
    """
    try:
        url = "https://www.instagram.com/{}/".format(username)
        headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": settings.INSTAGRAM_UA
        }
        if settings.INSTAGRAM_COOKIE:
            headers["Cookie"] = settings.INSTAGRAM_COOKIE
        page = requests.get(url, headers=headers)
        # Raise error for 404 cause by a bad profile name
        page.raise_for_status()
        return html.parse(page.content, treebuilder="dom")
    except HTTPError:
        logging.exception('user profile "{}" not found'.format(username))
    except (ConnectionError, socket_error) as e:
        logging.exception("instagram.com unreachable")


def instagram_profile_js(username):
    """
    Retrieve the script tags from the parsed page.
    :param username:
    :return:
    """
    try:
        tree = instagram_scrape_profile(username)
        return tree.getElementsByTagName("script")
    except AttributeError:
        logging.exception("scripts not found")
        return None


def instagram_profile_json(username):
    """
    Get the JSON data string from the scripts.
    :param username:
    :return:
    """
    scripts = instagram_profile_js(username)
    source = None

    if scripts:
        for script in scripts:
            if script.hasChildNodes():
                if script.firstChild.data[0:SCRIPT_JSON_PREFIX] == "window._sharedData":
                    source = script.firstChild.data[SCRIPT_JSON_DATA_INDEX:-1]

    return source


def instagram_profile_obj(username):
    """
    Retrieve the JSON from the page and parse it to a python dict.
    :param username:
    :return:
    """
    json_data = instagram_profile_json(username)

    return json.loads(json_data) if json_data else None
