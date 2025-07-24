"""
Service for Respond.IO API integration.
"""

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

RESPOND_IO_API_URL = getattr(settings, 'RESPOND_IO_API_URL', 'https://api.respond.io/v2')
RESPOND_IO_API_TOKEN = getattr(settings, 'RESPOND_IO_API_TOKEN', None)
RESPOND_IO_CHANNEL_ID = getattr(settings, 'RESPOND_IO_CHANNEL_ID', None)


def send_respondio_message(phone_number, message_type, content=None, file_url=None):
    """
    Send a message to a customer via Respond.IO API.
    message_type: 'text' or 'attachment'
    content: text content (for text messages)
    file_url: URL to file (for attachments)
    """
    if not RESPOND_IO_API_TOKEN:
        logger.error('Respond.IO API token not configured')
        return False, 'API token not configured'

    url = f"{RESPOND_IO_API_URL}/contact/phone:{phone_number}/message"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {RESPOND_IO_API_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'channelId': RESPOND_IO_CHANNEL_ID,
        'message': {}
    }
    if message_type == 'text':
        data['message'] = {
            'type': 'text',
            'text': content
        }
    elif message_type == 'attachment':
        data['message'] = {
            'type': 'attachment',
            'attachment': {
                'type': 'image' if file_url and file_url.lower().endswith(('jpg', 'jpeg', 'png')) else 'file',
                'url': file_url
            }
        }
    else:
        return False, 'Invalid message type'

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException as e:
        logger.error(f'Respond.IO API error: {e} | Data: {data}')
        return False, str(e) 