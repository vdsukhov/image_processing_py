import re

def convert_win_path_to_linux(path):
    """
    Function converts the windows path to wsl linux path
    
    Parameters:
    - path (str): window path (should be a raw string)
    
    Returns:
    (str): converted path for wsl system
    """
    
    prefix = re.match("^\w", path)[0].lower()
    prefix = f"/mnt/{prefix}"
    suffix = re.sub(r"^\w:", "", path)
    suffix = re.sub(r"\\+", "/", suffix)

    return f"{prefix}{suffix}"

