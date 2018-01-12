import requests


# FETCHING FUCTIONS
def prepare_session():
    """
    The Session object allows us to persist certain parameters across requests.
    """
    typical_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/59.0.3071.115 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
    }
    http_session = requests.Session()
    http_session.headers.update(typical_headers)
    return http_session


def fetch_url(url, parameters=None, additional_headers=None, session=None):
    """
    Download webpage by its URL.
    :param url: page url
    :param parameters: additional GET parameters
    :param additional_headers: headers for request
    :param session: which Session object to use
    :return: request's response object or None in case of errors
    """
    session = session or prepare_session()
    try:
        webpage_data = session.get(url, params=parameters, headers=additional_headers, timeout=20)
        webpage_data.raise_for_status()
    except requests.exceptions.RequestException:
        # TODO add logging here
        return None
    return webpage_data


def fetch_afisha_page():
    return fetch_url('https://www.afisha.ru/msk/schedule_cinema/')

# VALIDATING FUCTIONS


# PARCING FUCTIONS

if __name__ == '__main__':
    pass
