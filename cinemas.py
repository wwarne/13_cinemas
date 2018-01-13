import requests
from bs4 import BeautifulSoup

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


def fetch_kinopoisk(movie_name, http_session=None):
    ajax_headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }
    request_params = {
        'q': movie_name,
        'topsuggest': 'true',
        'ajax': 1
    }
    return fetch_url('https://www.kinopoisk.ru/search/suggest/',
                     additional_headers=ajax_headers,
                     parameters=request_params,
                     session=http_session)


def fetch_suggest_kinopoisk(movie_name, http_session=None):
    request_params = {
        'srv': 'kinopoisk',
        'part': movie_name
    }
    return fetch_url('https://suggest-kinopoisk.yandex.net/suggest-kinopoisk',
                     parameters=request_params,
                     session=http_session)


def fetch_movie_ranks(movie_id, http_session=None):
    return fetch_url('http://www.kinopoisk.ru/rating/{}.xml'.format(movie_id), session=http_session)


# VALIDATING FUCTIONS
def each_elem_has_keys(bunch_elements, keys_to_check):
    for element in bunch_elements:
        if not all(key in element for key in keys_to_check):
            return False
    return True


# PARCING FUCTIONS
def process_afisha_page(response_object):
    try:
        soup = BeautifulSoup(response_object.content.decode('utf-8'), 'lxml')
        movies = soup.find('div', id='schedule').find_all('div', class_='object')
    except AttributeError:
        # TODO add logging here
        return
    movies_info = []
    for movie in movies:
        try:
            rus_name = movie.find('h3').text
            cinemas_num = len(movie.find('table').find_all('tr'))
        except AttributeError:
            # Maybe html code has been changed
            # TODO add logging here
            continue
        else:
            movies_info.append(
                {
                    'rus_name': rus_name,
                    'cinemas_num': cinemas_num
                }
            )
    return movies_info


if __name__ == '__main__':
    pass
