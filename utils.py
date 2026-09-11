import re

def slugify(code: str) -> str:
    """
    Converts a string into a slug format.
    """
    code = code.strip().lower()
    code = re.sub(r'[^\w\s-]', '', code)
    code = re.sub(r'[\s_-]+', '-', code)
    code = re.sub(r'^-+|-+$', '', code)

    return code