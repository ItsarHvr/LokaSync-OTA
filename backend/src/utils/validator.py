import re

def validate_input(value: str) -> str:
    """
    Validate the input string to ensure it meets specific criteria.
    This to prevent from injection attacks and ensure consistency.

    Target input:
        - description,
        - node_location,
        - node_type,
        - node_id
    """
    # Check for invalid characters
    if not re.match(r"^[a-zA-Z0-9 _-]+$", value):
        raise ValueError("Input can only contain letters, numbers, spaces, underscores, and hyphens.")
    
    # Check for consecutive spaces or hyphens
    if "  " in value or "--" in value or "- -" in value or "-  -" in value:
        raise ValueError("Input cannot contain consecutive spaces or hyphens.")
    
    return value
    


def set_codename(node_location: str, node_type: str, node_id: str) -> str:
    """
    Generate a unique codename for a node based on its location, type, and ID.
    The codename is formatted as 'location-type-id'.
    """
    # Ensure all parts are lowercase and replace spaces with underscores
    if not all([node_location, node_type, node_id]):
        raise ValueError("Please provide valid values for node_location, node_type, and node_id, except for description.")
    
    location = node_location.lower().replace(" ", "")
    type = node_type.lower().replace(" ", "")
    id = node_id.lower().replace(" ", "")

    return f"{location}_{type}_{id}"