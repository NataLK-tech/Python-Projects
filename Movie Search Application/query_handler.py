# pip install tabulate

import random
from db_handler import get_connection
import tabulate

# func 1
def search_movies_by_keyword(keyword, option):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for fetching results as dict
    query = """
        SELECT title, genres, year, cast, `imdb.rating`, plot
        FROM movies
        WHERE title LIKE %s OR plot LIKE %s
    """
    params = (f"%{keyword}%", f"%{keyword}%")
    cursor.execute(query, params)
    results = cursor.fetchall()
    if option == 1:  # Top-5 Rated
        results.sort(key=lambda x: x['imdb.rating'], reverse=True)
        results = results[:5]
    elif option == 2:  # Randomly selected
        if len(results) > 0:
            results = random.sample(results, min(len(results), 5))
    else:
        raise ValueError
    cursor.close()
    connection.close()
    return results

# func 2
def search_movies_by_year(year, option):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT title, genres, year, cast, `imdb.rating`, plot
        FROM movies
        WHERE year = %s
    """
    cursor.execute(query, (year,))
    results = cursor.fetchall()
    if option == 1:  # Top-5 Rated
        results.sort(key=lambda x: x['imdb.rating'], reverse=True)
        results = results[:5]
    elif option == 2:  # Randomly selected
        if len(results) > 0:
            results = random.sample(results, min(len(results), 5))
    else:
        raise ValueError
    cursor.close()
    connection.close()
    return results

# func 3
def search_movies_by_genre(genre, option):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT title, genres, year, cast, `imdb.rating`, plot
        FROM movies
        WHERE genres LIKE %s
    """

    cursor.execute(query, (f"%{genre}%",))
    all_movies = cursor.fetchall()

    if option == 1:
        query_with_order = query + " ORDER BY `imdb.rating` DESC LIMIT 5"
        cursor.execute(query_with_order, (f"%{genre}%",))
        movies = cursor.fetchall()

    elif option == 2:
        movies = random.sample(all_movies, 5)
    else:
        raise ValueError
    cursor.close()
    connection.close()

    return movies

# func 4
def search_movies_by_year_and_genre(year, genre, option):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT title, genres, year, cast, `imdb.rating`, plot
        FROM movies
        WHERE year = %s AND genres LIKE %s
    """

    cursor.execute(query, (year, f"%{genre}%"))
    all_movies = cursor.fetchall()

    if option == 1:
        query_with_order = query + " ORDER BY `imdb.rating` DESC LIMIT 5"
        cursor.execute(query_with_order, (year, f"%{genre}%"))
        movies = cursor.fetchall()

    elif option == 2:
        movies = random.sample(all_movies, 5)
    else:
        raise ValueError
    cursor.close()
    connection.close()

    return movies

# func save
def save_search_query(query_text):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, count FROM popular_queries WHERE query = %s", (query_text,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE popular_queries SET count = count + 1, last_searched = CURRENT_TIMESTAMP WHERE id = %s",
                (existing['id'],)
            )
        else:
            cursor.execute("INSERT INTO popular_queries (query) VALUES (%s)", (query_text,))

        connection.commit()
    finally:
        cursor.close()
        connection.close()

# func 5
def get_popular_queries():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        query = "SELECT query, count FROM popular_queries ORDER BY count DESC LIMIT 5;"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def choose_genre():
    data = [
        ["\u001b[32;1m CHOOSE A GENRE: \u001b[0m", "Action", "Adventure", "Animation", "Biography"],
        [" ", "Comedy", "Crime", "Documentary", "Drama"],
        [" ", "Family", "Fantasy", "History", "Horror"],
        [" ", "Music", "Musical", "Mystery", "News"],
        [" ", "Romance", "Sci-Fi", "Short", "Sport"],
        [" ", "Thriller", "War", "Western"]
    ]
    results = tabulate.tabulate(data)
    print(results)

def choose_year():
    data_year = [
        ["\u001b[32;1m CHOOSE A YEAR: \u001b[0m", "2007", "2008", "2009"],
        [" ", "2010", "2011", "2012"],
        [" ", "2013", "2014", "2015"]
    ]
    results_year = tabulate.tabulate(data_year)
    print(results_year)

