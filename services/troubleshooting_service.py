from .pdf_processing import extract_images_and_text_from_pdf
from .oai import create_openai_chat_request, process_openai_response
import openai
import json

from sanic import Sanic
from sanic.response import text, json as sanic_json
import json
import os
import openai
import requests
import tempfile
from urllib.parse import urlparse
import base64
from PIL import Image
import io
import tiktoken

from app.config import Config
from models.response import TroubleshootingData
from services.oai import create_openai_chat_request, process_openai_response
from services.pdf_processing import extract_images_and_text_from_pdf

openai.api_version = Config.OPENAI_API_VERSION
openai.api_type = Config.OPENAI_API_TYPE
openai.organization = Config.OPENAI_ORGANIZATION
openai.api_key = Config.OPENAI_API_KEY
openai.api_base = Config.OPENAI_API_BASE
#INPUT + OUTPUT TOKENS CAN BE MAX 128000
MAX_ALLOWED_TOKENS=Config.MAX_ALLOWED_TOKENS
REQUESTED_OUTPUT_TOKENS=Config.REQUESTED_OUTPUT_TOKENS
# Define the image size limit in bytes for 20 MB
IMAGE_SIZE_LIMIT = Config.IMAGE_SIZE_LIMIT  # 20 MB in bytes








def extract_troubleshoot_pdf(pdf_full_path):
    """Run the entire conversation process."""

    images_data_urls, data_pages = extract_images_and_text_from_pdf(pdf_full_path)

    json_arr_to_return = []
    for imageId, image_data_url in enumerate(images_data_urls, start=0):
        messages, number_of_tokens = create_openai_chat_request(image_data_url)
        if number_of_tokens > MAX_ALLOWED_TOKENS - REQUESTED_OUTPUT_TOKENS:
            print("Skipping the page, too many tokens in the page than allowed")
            continue
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-vision-preview",
            messages=messages,
            temperature=1,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            tools=TroubleshootingData.RESPONSE_SCHEMA,
            seed=12345,
            tool_choice={"type": "function", "function": {"name": "save_troubleshooting_data"}}
        )

        response_message = response.choices[0].message
        results = process_openai_response(response_message,data_pages[imageId])

        if len(results)>0:
            json_arr_to_return.extend(results)
    return json_arr_to_return


def assign_ids_to_conditions(troubleshooting_section):
    """
    Assigns a unique primary ID and a group ID based on condition to each troubleshooting object.

    :param troubleshooting_section: A list of dictionaries, each containing a list of troubleshooting objects.
    """
    condition_to_id = {}
    current_group_id = 1
    current_primary_id = 1

    # Iterate through each page in the troubleshooting section
    for page in troubleshooting_section:
        # Iterate through each troubleshooting object on the page
        for obj in page["troubleshooting_objects_array"]:
            condition = obj["conditionOrProblem"]

            # Assign a unique primary ID to each object
            obj["primaryId"] = current_primary_id
            current_primary_id += 1

            # Check if the condition has been encountered before
            if condition not in condition_to_id:
                # If it's a new condition, assign a new group ID and map it
                condition_to_id[condition] = str(current_group_id)
                obj["troubleshootinggroupManualID"] = int(condition_to_id[condition])
                current_group_id += 1
            else:
                # If the condition is already mapped, use the existing group ID
                obj["troubleshootinggroupManualID"] = int(condition_to_id[condition])

    return troubleshooting_section


