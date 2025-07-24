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


def assign_customer_respondio(phone_number, assignee_email):
    """
    Assign a customer to a user via Respond.IO API.
    """
    if not RESPOND_IO_API_TOKEN:
        logger.error('Respond.IO API token not configured')
        return False, 'API token not configured'

    url = f"{RESPOND_IO_API_URL}/contact/phone:{phone_number}/conversation/assignee"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {RESPOND_IO_API_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'assignee': assignee_email
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException as e:
        logger.error(f'Respond.IO assignment API error: {e} | Data: {data}')
        return False, str(e)


def unassign_customer_respondio(phone_number):
    """
    Unassign a customer via Respond.IO API.
    """
    if not RESPOND_IO_API_TOKEN:
        logger.error('Respond.IO API token not configured')
        return False, 'API token not configured'

    url = f"{RESPOND_IO_API_URL}/contact/phone:{phone_number}/conversation/assignee"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {RESPOND_IO_API_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'assignee': None
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException as e:
        logger.error(f'Respond.IO unassignment API error: {e} | Data: {data}')
        return False, str(e)


def upload_file_to_respondio(file_path):
    """
    Upload a file to Respond.IO for later use in messages.
    This is a simplified version for MVP - in production, you'd upload to your file storage first.
    """
    # For MVP, we'll assume files are already accessible via URL
    # In production, this would upload to your CDN/S3 and return the URL
    logger.info(f'File upload to Respond.IO: {file_path}')
    return True, {'file_url': file_path}


def send_file_to_customer_respondio(phone_number, file_url, file_type='file'):
    """
    Send a file to a customer via Respond.IO API.
    """
    return send_respondio_message(phone_number, 'attachment', file_url=file_url)


def create_internal_comment_respondio(phone_number, comment_text, tagged_user_ids=None):
    """
    Create an internal comment via Respond.IO API.
    """
    if not RESPOND_IO_API_TOKEN:
        logger.error('Respond.IO API token not configured')
        return False, 'API token not configured'

    url = f"{RESPOND_IO_API_URL}/contact/phone:{phone_number}/comment"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {RESPOND_IO_API_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    # Format comment with user tags
    formatted_text = comment_text
    if tagged_user_ids:
        for user_id in tagged_user_ids:
            formatted_text += " {{@user." + str(user_id) + "}} "

    data = {
        'text': formatted_text
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException as e:
        logger.error(f'Respond.IO comment API error: {e} | Data: {data}')
        return False, str(e) 