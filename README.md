# Cinemas

This script is finding top movies currently running in cinemas according to their Kinopoisk rating.

# How to use

1. Run command `python cinemas.py`
2. Wait and you'll get the result like this:
```
Fetching a webpage from Afisha.ru
Grabbing information about every movie.
+-------+-----------------------------------------------------------+---------+
|  Rank | Name                                                      | Cinemas |
+-------+-----------------------------------------------------------+---------+
| 8.377 | Движение вверх (Движение вверх)                           |   152   |
| 8.339 | Приключения Паддингтона&nbsp;2 (Paddington 2)             |   162   |
| 7.869 | Величайший шоумен (The Greatest Showman)                  |    51   |
| 7.514 | Темные времена (Darkest Hour)                             |    57   |
| 7.511 | Фердинанд (Ferdinand)                                     |    45   |
| 7.394 | Карп отмороженный (Карп отмороженный)                     |    35   |
| 7.383 | Форма воды (The Shape of Water)                           |   128   |
| 7.096 | Джуманджи: Зов джунглей (Jumanji: Welcome to the Jungle)  |    58   |
| 7.096 | Праздничный переполох (Le sens de la fête)                |    13   |
| 7.079 | Большая игра (State of Play)                              |    49   |
+-------+-----------------------------------------------------------+---------+

```


# Build with

* [Requests](http://docs.python-requests.org/en/master/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [LXML](http://lxml.de/)
* [PTable](https://pypi.python.org/pypi/PTable/0.9.0)

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
