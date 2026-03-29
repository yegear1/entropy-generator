from loguru import logger

import secrets
import string
import emoji
import os

def generate_password(length: int, use_upper=True, use_lower=True, use_digits=True, use_specials=True, use_emojis=False) -> str:
    """
    Generates a secure, random password of a specified length and character composition.

    This function creates a password by combining different character types as specified by the
    boolean flags. It ensures that at least one character from each selected type is included
    in the final password. The remaining characters are chosen randomly from the combined pool
    of allowed characters, and the final result is securely shuffled.

    Args:
        length (int): The total desired length of the password.
        use_upper (bool, optional): If True, include uppercase letters (A-Z). Defaults to True.
        use_lower (bool, optional): If True, include lowercase letters (a-z). Defaults to True.
        use_digits (bool, optional): If True, include digits (0-9). Defaults to True.
        use_specials (bool, optional): If True, include special punctuation characters. Defaults to True.
        use_emojis (bool, optional): If True, include emoji characters. Defaults to False.

    Returns:
        str: The generated password as a string.

    Raises:
        ValueError:
            - If no character types are selected (e.g., all boolean flags are False).
            - If the specified `length` is less than the number of selected character types,
              making it impossible to guarantee one of each type.
    """
    characters = ""
    guaranteed_characters = []
    password_finals = []

    if use_upper:
        characters += string.ascii_uppercase
        guaranteed_characters.append(secrets.choice(string.ascii_uppercase))
    if use_lower:
        characters += string.ascii_lowercase
        guaranteed_characters.append(secrets.choice(string.ascii_lowercase))
    if use_digits:
        characters += string.digits
        guaranteed_characters.append(secrets.choice(string.digits))
    if use_specials:
        characters += string.punctuation # Caracteres especiais do py.strings
        guaranteed_characters.append(secrets.choice(string.punctuation))
    if use_emojis:
        emoji_list = list(emoji.EMOJI_DATA.keys())

        characters += "".join(emoji_list)
        guaranteed_characters.append(secrets.choice(emoji_list))

    if not characters:
        logger.error("At least one character type must be included")
        raise ValueError("At least one character type must be included")
    
    if length < len(guaranteed_characters):
        logger.error(f"Length too short. Need at least {len(guaranteed_characters)} for selected types.")
        raise ValueError(f"Length too short. Need at least {len(guaranteed_characters)} for selected types.")
    
    remnant_length = length - len(guaranteed_characters)
    password_finals = [secrets.choice(characters) for _ in range(remnant_length)]

    final_password = password_finals + guaranteed_characters
    secrets.SystemRandom().shuffle(final_password)

    return ''.join(final_password)

def generate_passphrase(length: int, language: str='en') -> str:
    """
    Generates a passphrase of a specified length using words from a language-specific wordlist.

    This function creates a memorable passphrase by randomly selecting a specified number of words
    from a wordlist file corresponding to the chosen language. The words are then joined together
    with hyphens to form the final passphrase.

    The wordlists are expected to be in the `data/` directory relative to the project root,
    with one word per line, potentially preceded by an index or number which is ignored.

    Args:
        length (int): The number of words to include in the passphrase.
        language (str, optional): The language of the wordlist to use. 
                                  Supported values are 'en' for English and 'pt' for Portuguese.
                                  Defaults to 'en'.

    Returns:
        str: A hyphen-separated passphrase string composed of randomly chosen words.
    """
    # Resolve o caminho relativo à raiz do backend (2 níveis acima deste arquivo)
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")

    if language == "pt":
        file_path = os.path.join(base_dir, "portuguese.wordlist.txt")
    elif language == "en":
        file_path = os.path.join(base_dir, "english_wordlist.txt")
    else:
        raise ValueError(f"Unsupported language: {language}")

    with open(file_path, 'r', encoding='utf-8') as file:
        wordlist = []
        for line in file:
            partes = line.split()
            if len(partes) >= 2:
                wordlist.append(partes[1])
                
        return '-'.join(secrets.choice(wordlist) for _ in range(length))
