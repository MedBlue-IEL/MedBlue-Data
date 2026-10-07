import re
import unidecode

def remove_accents(string):
    string = re.sub(u"[àáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîï]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    string = re.sub(u"[ýÿ]", 'y', string)
    return string

def generate_clean_code(value: str) -> str:
    """Automatically converts the project_code to uppercase."""
    if isinstance(value, str):
        no_accents = remove_accents(value.lower().strip())
        replace_spaces = no_accents.replace("  ", " ").replace(" ", "_")
        no_special_chars = re.sub(r'[^A-Za-z0-9_-]+', '', replace_spaces)
        ascii_value = unidecode.unidecode(no_special_chars)
        cleanup_spaces = (ascii_value.replace("--", "-")
                          .replace("_-", "_")
                          .replace("-_", "_")
                          .replace("__", "_")
                          .replace("__", "_")
                          .replace("_", " ")
                          .strip().replace(" ", "_"))
        value = cleanup_spaces.upper()
    return value