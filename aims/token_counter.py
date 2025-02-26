import tiktoken

def count_tokens_in_file(file_path: str, enc: str = "gpt-4o") -> int:
    """
    Count the number of tokens in a file.

    Args:
        file_path (str): The path to the file to count tokens in.
        enc (str, optional):  The encoding model to use. Defaults to "gpt-4o".

    Returns:
        int: The number of tokens in the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f: text_data = f.read()
    return count_tokens(text_data, enc)



def count_tokens(txt:str,enc:str="gpt-4o-mini") -> int:
    """
    Count the number of tokens in a given text string.

    Args:
        txt (str): The text string to count tokens in.

    Returns:
        int: The number of tokens in the string.
    """
    encoding = tiktoken.encoding_for_model(enc)
    tokens = encoding.encode(txt)
    return len(tokens)