from utils.token_counter import count_tokens
import json
def save_troubleshooting_data(troubleshooting_objects_array, page_num, bypass="FALSE"):
    """Save troubleshooting data into a structured format."""
    if bypass == "TRUE":
        return None
    else:
        return {
            "page_num": page_num,
            "troubleshooting_objects_array": troubleshooting_objects_array
        }


def create_openai_chat_request(image_data_url):
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
    return "LLM didn't want to call the function this will probably never run because we force it to call function"