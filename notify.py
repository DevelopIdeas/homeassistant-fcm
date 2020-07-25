"""Notification support for Fcm."""
import argparse
import json
import requests
import datetime

import logging

import voluptuous as vol

from homeassistant.components.notify import (
  ATTR_DATA,
  PLATFORM_SCHEMA,
  BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.template as template_helper

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'fcm'
ATTR_TITLE = 'title'
ATTR_MESSAGE = 'message'
ATTR_TYPE = 'type'
ATTR_SERVER_KEY = 'server_key'
ATTR_TOPIC = 'topic'

BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'fcm/send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT

def get_service(hass, config, discovery_info=None):
  """Get the Fcm notification service."""
  data = {
    ATTR_SERVER_KEY: None,
    ATTR_TOPIC: None
  }
  if ATTR_SERVER_KEY in config:
      data[ATTR_SERVER_KEY] = config[ATTR_SERVER_KEY]
  if ATTR_TOPIC in config:
      data[ATTR_TOPIC] = config[ATTR_TOPIC]

  return FcmNotificationService(hass, data)

class FcmNotificationService(BaseNotificationService):
    """Implement the notification service for Fcm."""

    def __init__(self, hass, data):
        """Initialize the service."""
        self.hass = hass
        self.data = data

    def send_message(self, message="", **kwargs):
        """Send a notification to the device."""
        _LOGGER.info('Fcm send_message')

        data = dict(kwargs.get(ATTR_DATA) or {})
        msg_title = kwargs.get(ATTR_TITLE, '')
        msg_type = data.get(ATTR_TYPE, '')

        msg = self._build_common_message(msg_title, message, msg_type)

        res = self._send_fcm_message(msg)
        return res

    def _send_fcm_message(self, fcm_message):
        """Send HTTP request to FCM with given message.
        Args:
          fcm_message: JSON object that will make up the body of the request.
        """
        # [START use_access_token]
        headers = {
           'Authorization': 'key=' + self.data[ATTR_SERVER_KEY],
            'Content-Type': 'application/json; UTF-8',
        }
        # [END use_access_token]
        resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

        _LOGGER.debug("Request answer, Status Code: " + str(resp.status_code))
        _LOGGER.debug("Request answer, Text: " + resp.text)

        if resp.status_code == 200:
            print('Message sent to Firebase for delivery, response:')
            print(resp.text)
            return True
        else:
            print('Unable to send message to Firebase')
            print(resp.text)
            return False

    def _build_common_message(self, msg_title, msg_text, msg_type):
        """Construct common notifiation message.
        Construct a JSON object that will be used to define the
        common parts of a notification message that will be sent
        to any app instance subscribed to the news topic.
        """
        data = {
            "notification": {
                "title": "",
                "body": "",
                "image": None,
                "visibility": 1,
                "sound": "default"
            },
            "data": {
                "type": "home"
            },
            "apns": {
                "payload": {
                    "aps": {
                        "mutable-content": 1
                    }
                },
                "fcm_options": {
                    "image": ""
                }
            },
            "android": {
                "priority": "high"
            },
            "priority": "high",
            "to": None
        }
        data['to'] = "/topics/"+self.data[ATTR_TOPIC]
        data['notification']['title'] = msg_title
        data['notification']['body'] = msg_text
        data['data']['type'] = msg_type
        _LOGGER.debug(data)
        return data
