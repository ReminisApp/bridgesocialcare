import tiktoken
def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4")
    data_text = text
    num_tokens = len(encoding.encode(data_text, disallowed_special=()))
    return num_tokens