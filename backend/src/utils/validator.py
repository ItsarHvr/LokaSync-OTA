import re
from html import escape

def sanitize_input(value: str) -> str:
    """
    Sanitize the input string to prevent XSS attacks and ensure safe HTML rendering.
    This function escapes HTML special characters to prevent injection attacks.
    
    Target input is only for `description`, which is flexible but needs to be safe for HTML rendering.
    """
    ALLOWED_CHARS_REGEX = re.compile(r"^[\w\s.,:;!?()\-_/']*$")  # <-- changed + to *
    value = escape(value)
    value = re.sub(r"[\x00-\x1f\x7f]", "", value)
    if not ALLOWED_CHARS_REGEX.fullmatch(value):
        raise ValueError("Description contains invalid characters.")
    return value

def validate_input(value: str) -> str:
    """
    Validate the input string to ensure it meets specific criteria.
    This to prevent from injection attacks and ensure consistency.

    Target input:
        - node_location,
        - node_type,
        - node_id
    """
    # Disallow spaces
    if " " in value:
        raise ValueError("Input cannot contain spaces.")

    # Check for invalid characters
    if not re.match(r"^[a-zA-Z0-9_-]+$", value):
        raise ValueError("Input can only contain letters, numbers, underscores, and hyphens.")

    # Check for consecutive hyphens
    if "--" in value or "- -" in value or "-  -" in value:
        raise ValueError("Input cannot contain consecutive hyphens.")

    return value

def set_codename(node_location: str, node_type: str, node_id: str) -> str:
    """
    Generate a unique codename for a node based on its location, type, and ID.
    
    The node_codename is formatted as 'location-type-id'.
    """
    if not all([node_location, node_type, node_id]):
        raise ValueError("Please provide valid values for node_location, node_type, and node_id, except for description.")
    
    location = node_location.lower().replace(" ", "")
    type = node_type.lower().replace(" ", "")
    id = node_id.lower().replace(" ", "")

    return f"{location}_{type}_{id}"