import re
from html import escape
from urllib.parse import urlparse

def sanitize_input(value: str) -> str:
    """
    Sanitize the input string to prevent XSS attacks and ensure safe HTML rendering.
    This function escapes HTML special characters to prevent injection attacks.
    
    Target input is only for `description`, which is flexible but needs to be safe for HTML rendering.
    """
    ALLOWED_CHARS_REGEX = re.compile(r"^[\w\s.,:;!?()\-_/']*$")
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

def validate_url(value: str) -> str:
    """
    Validate the input string to ensure it is a valid URL.
    This function checks if the URL starts with http:// or https://.
    """
    if isinstance(value, str) and value.strip() == "":
        return None
    
    parsed = urlparse(value)

    # Check if scheme is present and valid
    if not parsed.scheme:
        raise ValueError("URL must include a protocol (http:// or https://).")
        
    if parsed.scheme not in ['http', 'https']:
        raise ValueError("URL must start with 'http://' or 'https://'.")
    
    # Check if netloc (domain) is present
    if not parsed.netloc:
        raise ValueError("URL must contain a valid domain.")
    
    # More robust domain validation
    domain = parsed.netloc.lower()
    
    # Remove port if present
    if ':' in domain:
        domain = domain.split(':')[0]
    
    # Check for localhost and IP addresses (allowed for development)
    if domain in ['localhost', '127.0.0.1'] or domain.startswith('192.168.') or domain.startswith('10.'):
        return value  # Allow local development URLs
    
    # For production domains, require TLD
    if '.' not in domain:
        raise ValueError("URL must contain a valid domain with TLD (e.g., .com, .org).")
    
    # Check for valid domain format
    domain_parts = domain.split('.')
    if len(domain_parts) < 2:
        raise ValueError("URL must contain a valid domain with TLD (e.g., .com, .org).")
        
    # Check for empty domain parts
    if any(not part for part in domain_parts):
        raise ValueError("Invalid domain format.")
    
    # Basic domain name validation
    domain_regex = re.compile(r'^[a-zA-Z0-9.-]+$')
    if not domain_regex.match(domain):
        raise ValueError("Domain contains invalid characters.")
    
    # Return the validated URL as string
    return value.strip()

def validate_version(value: str) -> str:
    """
    Validate the input string to ensure it is a valid version format.
    The version should be in the format x.y.z where x, y, and z are integers.
    """
    # Check if the value is match the version format and has a minimum length
    if not re.match(r'^\d+\.\d+\.\d+$', value) and len(value.strip()) < 5:
        raise ValueError("Version must be in semantic versioning format: x.y.z")
    
    return value.strip()

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