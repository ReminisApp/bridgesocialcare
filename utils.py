from sanic import Sanic
from sanic.response import text, json as sanic_json
import json
import os
import openai
import requests
import tempfile
from urllib.parse import urlparse


openai.api_version = "2020-11-07"
openai.api_type = "open_ai"
openai.organization = "org-2NSCKElNkP4xGwyheiFVhjsX"
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = "https://api.openai.com/v1"
import base64
from PIL import Image
import io
from PyPDF2 import PdfReader, PdfWriter
import tiktoken


#INPUT + OUTPUT TOKENS CAN BE MAX 128000
MAX_ALLOWED_TOKENS=128000
REQUESTED_OUTPUT_TOKENS=4096
# Define the image size limit in bytes for 20 MB
IMAGE_SIZE_LIMIT = 20 * 1024 * 1024  # 20 MB in bytes


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4")
    data_text = text
    num_tokens = len(encoding.encode(data_text, disallowed_special=()))
    return num_tokens

def save_troubleshooting_data(troubleshooting_objects_array, page_num, bypass="FALSE"):
    """Save troubleshooting data into a structured format."""
    if bypass == "TRUE":
        return None
    else:
        return {
            "page_num": page_num,
            "troubleshooting_objects_array": troubleshooting_objects_array
        }

def extract_images_and_text_from_pdf(pdf_path):
    """Extract images from a given PDF file and return them as a list of base64-encoded data URLs."""
    pdf = PdfReader(pdf_path)
    images_data_urls = []
    data_pages = []
    text_data = []

    for page_number, page in enumerate(pdf.pages, start=1):
        # Extract text from the current page
        text_on_page = page.extract_text()

        for image in page.images:
            with open("/tmp/"+image.name, "wb") as fp:
                fp.write(image.data)
                file_path = "/tmp/"+image.name
                file_size = os.path.getsize(file_path)

                # Check if the file size is greater than 20 MB
                if file_size > IMAGE_SIZE_LIMIT:
                    print(f"Skipping this image, image in the pdf with page number {page_number} is larger than 20 MB.")
                    continue

                with open(file_path, "rb") as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode("utf-8")
                    data_url = f"data:image/jpeg;base64,{encoded_image}"
                    images_data_urls.append(data_url)
                    data_pages.append(page_number)
                    text_data.append(text_on_page)
                    os.remove(file_path)

    return images_data_urls,data_pages,text_data

def create_openai_chat_request(image_data_url, text_data):
    """Create a chat request to the OpenAI client with the given image data URL."""
    prompt = "You are a helpful assistant that detects troubleshoot sections in a product manual. Firstly you should strictly make sure that all available fields required to make the function call can be reasonably filled in from the image. Secondly step by step and line by line, detect if there is a troubleshooting section as a table in the given image. If so, call the function with BYPASS FALSE and correct function arguments to fill in the spreadsheet properly. There should be a keyword as title or subtitle explaining that it's a troubleshooting section. I will tip you $1000 if you never miss any detail and work like it's wednesday. To make sure there is a table check lines, columns and rows they should be obvious otherwise set bypass equals 'TRUE' for corpus and non-table elements."

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text",
                 "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": image_data_url}}
            ],
        }
    ]

    #IMAGE URL IS NOT INCLUDED IN THE TOKEN CALCULATION BECAUSE IT HAS SEPARATE 20MB LIMIT
    number_of_tokens = count_tokens(json.dumps( {
            "role": "user",
            "content": [
                {"type": "text",
                 "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": ""}}
            ],
        }))
    return messages, number_of_tokens


def process_openai_response(response_message,page_num):
    """Process the OpenAI response and potentially initiate another round of processing based on the tool calls."""
    tool_calls = response_message.tool_calls
    if tool_calls:
        available_functions = {"save_troubleshooting_data": save_troubleshooting_data}
        results = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            # Initial function response based on first tool call
            function_response = function_to_call(
                troubleshooting_objects_array=function_args.get("troubleshooting_objects_array"),
                bypass=function_args.get("bypass"),
                page_num=page_num
            )
            if function_response:
                results.append(function_response)

        return results
    return "LLM didn't want to call the function"


def extract_troubleshoot_pdf(pdf_full_path):
    """Run the entire conversation process."""

    images_data_urls, data_pages, text_data = extract_images_and_text_from_pdf(pdf_full_path)

    json_arr_to_return = []
    for imageId, image_data_url in enumerate(images_data_urls, start=0):
        messages, number_of_tokens = create_openai_chat_request(image_data_url,text_data[imageId])
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
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "save_troubleshooting_data",
                        "description": "If a table is given generate an array of problem , possibleCause , proposedSolution triples. IF THERE IS NO TROUBLESHOOTING INFORMATION IN THE GIVEN IMAGE SEND BYPASS AS 'TRUE' . A problem might have multiple causes and a cause might have multiple ways to solutions which can repeat. That's why problem and possible cause can repeat multiple times in the given arrays. Possible array parameters can be like below  ID:['1','2','3','4', '5'], conditionOrProblem: ['boiler is not working','boiler is not working','boiler is not working','boiler never powers on', 'boiler gives error code 400'] , possibleCauseOrThingsToCheck: ['Boiler plug', 'Power indicator', 'Power ON button on the boiler', 'Gas valve', 'Water supply valve'] , proposedSolution: ['Plug the boiler to give electricity', 'If it's given yellow light it means this boiler is not for your electricity type', 'Make sure your power on button is switched to ON', 'Turn gas valve to right to give gas supply', 'Turn water valve to right to give water supply'] ",

                        "parameters": {
                            "type": "object",
                            "properties": {
                                "troubleshooting_objects_array": {
                                    "type": "array",
                                    "description": "Array of objects each object refers to a unique virtual troubleshooting instance",
                                    "items": {
                                        "type": "object",
                                        "properties": {

                                            "conditionOrProblem": {
                                                "type": "string",
                                                "description": "Array of problems you can repeat the same item if same problem has multiple causes and multiple solutions"
                                            },

                                            "possibleCauseOrThingsToCheck": {
                                                "type": "string",
                                                "description": "Possible cause or things to check to solve the problem this field can also repeat"
                                            },
                                            "proposedSolution": {
                                                "type": "string",
                                                "description": "Solution candidate of the given problem and possible cause"
                                            },
                                            "pageNumberShownToHuman": {
                                                "type": "string",
                                                "description": "Page number that exists in the image. Only fill if exists otherwise leave empty by setting ''. Optional. "
                                            },
                                        }
                                    },

                                },
                                "bypass": {
                                    "type": "string",
                                    "description": "Set to 'TRUE' if there is no troubleshooting table in the view. "
                                }
                            },
                            "required": ["troubleshooting_objects_array",
                                         "bypass"],
                        },
                    },
                }
            ],
            seed=12345,
            tool_choice={"type": "function", "function": {"name": "save_troubleshooting_data"}}
        )

        response_message = response.choices[0].message
        results = process_openai_response(response_message,data_pages[imageId])

        if len(results)>0:
            json_arr_to_return.extend(results)
    return json_arr_to_return


