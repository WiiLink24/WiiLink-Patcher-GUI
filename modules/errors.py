import socket
import traceback
from urllib.error import HTTPError


def error_handler(error: Exception) -> str:
    """
    Takes an exception, and returns a nice error message suitable for end users.

    Args:
        error: The exception to review.

    Returns:
        str: The error message.
    """
    try:
        raise error
    except TimeoutError:
        return "A timeout occurred. Check our <a href=https://status.wiilink.ca>server status</a>. If everything looks fine, check your Internet connection is working properly."
    except HTTPError:
        return f"{error}. Check our <a href=https://status.wiilink.ca>server status</a>. If everything looks fine, check your Internet connection is working properly."
    except ConnectionResetError:
        return f"{error}. Check our <a href=https://status.wiilink.ca>server status</a>. If everything looks fine, check your Internet connection is working properly."
    except socket.gaierror:
        return "A failure occurred in name resolution. Check your Internet connection is working properly."
    except:
        return traceback.format_exc()
