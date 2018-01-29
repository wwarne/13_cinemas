import requests
import json
import sys
from bs4 import BeautifulSoup
from lxml import etree
from prettytable import PrettyTable


def prepare_session():
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
    session = session or prepare_session()
    try:
        webpage_data = session.get(url, params=parameters, headers=additional_headers, timeout=20)
        webpage_data.raise_for_status()
    except requests.exceptions.RequestException:
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


def process_afisha_page(response_object):
    try:
        soup = BeautifulSoup(response_object.content.decode('utf-8'), 'lxml')
        movies = soup.find('div', id='schedule').find_all('div', class_='object')
    except AttributeError:
        return
    movies_info = []
    for movie in movies:
        try:
            rus_name = movie.find('h3').text
            cinemas_num = len(movie.find('table').find_all('tr'))
        except AttributeError:
            continue
        else:
            movies_info.append(
                {
                    'rus_name': rus_name,
                    'cinemas_num': cinemas_num
                }
            )
    return movies_info


def process_kinopoisk_page(response_object):
    try:
        info = response_object.json(encoding='utf-8')
    except ValueError:
        # TODO add logging here
        return False
    if not isinstance(info, list):
        return None
    # Determine what have we got here. I've already faced two types of server answers.
    if each_elem_has_keys(info, ('dataType',)):
        return extract_from_kp_ver2(info)
    if each_elem_has_keys(info, ('id', 'name', 'year', 'rus')):
        return extract_from_kp_ver1(info)


def extract_from_kp_ver1(films_data):
    only_films = [film for film in films_data if film.get('is_serial') != 'serial' and film.get('ur_rating')]
    sorted_films = sorted(only_films, key=lambda elem: int(elem.get('year', 0)), reverse=True)
    return {
        'id': sorted_films[0]['id'],
        'kp_rank': sorted_films[0]['ur_rating'],
        'original_name': sorted_films[0]['name'],
        'rus_name': sorted_films[0]['rus']
    }


def extract_from_kp_ver2(films_data):
    only_films = [film for film in films_data if films_data['dataType'] == 'film']
    sorted_films = sorted(only_films, key=lambda elem: int(elem['year']), reverse=True)
    return {
        'id': sorted_films[0]['id'],
        'kp_rank': sorted_films[0]['rating']['value'],
        'original_name': sorted_films[0]['name'],
        'rus_name': sorted_films[0]['rus']
    }


def extract_from_suggest_kp(films_data):
    only_fimls = [film for film in films_data if film.get('type') == 'MOVIE']
    sorted_films = sorted(only_fimls, key=lambda elem: max(elem.get('years', [0])), reverse=True)
    result = {
        'id': sorted_films[0]['entityId'],
        'original_name': sorted_films[0]['originalTitle'],
        'rus_name': sorted_films[0]['title']
    }
    if sorted_films[0].get('rating'):
        result['kp_rank'] = sorted_films[0]['rating']['rate']
        result['kp_votes'] = sorted_films[0]['rating']['votes']
    return result


def process_suggest_kinopoisk(response_object):
    try:
        info = response_object.json(encoding='utf-8')
        search_result = list(map(json.loads, info[2]))
    except AttributeError:
        # Битый json пришёл в ответ
        return
    except IndexError:
        # Изменился формат ответа?
        return
    if not each_elem_has_keys(search_result, ('entityId',)):
        return
    return extract_from_suggest_kp(search_result)


def process_movie_ranks(response_object):
    ranks_data = etree.fromstring(response_object.content)
    kp_rating = ranks_data.find('kp_rating')
    imdb_rating = ranks_data.find('imdb_rating')
    result = {}
    if kp_rating is not None:
        result['kp_rank'] = float(kp_rating.text)
        result['kp_votes'] = int(kp_rating.get('num_vote'))
    if imdb_rating is not None:
        result['imdb_rank'] = float(imdb_rating.text)
        result['imdb_votes'] = int(imdb_rating.get('num_vote'))
    return result


def print_movies(movies_data, num_to_print=10):
    x = PrettyTable()
    x.field_names = ['Rank', 'Name', 'Cinemas']
    x.align['Name'] = 'l'
    result = sorted(movies_data, key=lambda elem: float(elem['kp_rank']), reverse=True)[:num_to_print]
    for movie in result:
        x.add_row([movie['kp_rank'], movie['rus_name'] + ' (' + movie['original_name'] + ') ', movie['cinemas_num']])
    print(x)


def search_movie_info(one_movie):
    movie_page = fetch_kinopoisk(movie_name=one_movie['rus_name'], http_session=kp_session)
    movie_data = process_kinopoisk_page(movie_page)
    if not movie_data:
        movie_page = fetch_suggest_kinopoisk(movie_name=one_movie['rus_name'], http_session=kp_suggest_session)
        movie_data = process_suggest_kinopoisk(movie_page)
    if not movie_data:
        # We failed to get data from both kinopoisk websites.
        return []
    movie_rank_page = fetch_movie_ranks(movie_id=movie_data['id'], http_session=kp_ranks_session)
    movie_ranks = process_movie_ranks(movie_rank_page)
    one_movie.update(movie_data)
    one_movie.update(movie_ranks)
    return one_movie


if __name__ == '__main__':
    kp_session = prepare_session()
    kp_suggest_session = prepare_session()
    kp_ranks_session = prepare_session()
    print('Fetching a webpage from Afisha.ru')
    afisha_page = fetch_afisha_page() or sys.exit('Website Afisha.ru not found')
    movies_from_afisha = process_afisha_page(afisha_page) or sys.exit('Probably Afisha\'s layout has been changed.')
    interesting_movies = sorted(movies_from_afisha, key=lambda elem: elem['cinemas_num'], reverse=True)[:20]
    print('Grabbing information about every movie.')
    movies_information = [search_movie_info(movie) for movie in interesting_movies]
    print_movies(movies_information)
