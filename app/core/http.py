import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from .config import get_settings

def get_session() -> requests.Session:
    s = requests.Session()
    st = get_settings()

    retries = Retry(
        total=st.HTTP_RETRY_TOTAL,
        backoff_factor=st.HTTP_RETRY_BACKOFF,
        status_forcelist=(502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=st.HTTP_POOL_SIZE, pool_maxsize=st.HTTP_POOL_SIZE)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s