from query_handler import (
    search_movies_by_keyword,
    search_movies_by_year,
    search_movies_by_year_and_genre,
    search_movies_by_genre,
    save_search_query,
    get_popular_queries,
    choose_genre,
    choose_year
)


def main():
    print("\n\u001b[32;1m  WELCOME TO THE MOVIE SEARCH APPLICATION !!! \u001b[0m")
    while True:
        print("\n\t\t\u001b[33;1m Possible commands: \u001b[0m")
        print("1. Search movies by keyword")
        print("2. Search movies by year")
        print("3. Search movies by genre")
        print("4. Search movies by year and genre")
        print("5. Show popular queries")
        print("6. Exit")

        choice = input("\n\u001b[33;1m Enter your choice: \u001b[0m")

        if choice == "1":
            keyword = input("\t\u001b[33m Enter keyword:\u001b[0m")
            print("Select an option:")
            print("1. Top-5 Rated Movies")
            print("2. Randomly Selected Movies")
            try:
                option = int(input("\t\u001b[33m Enter 1 or 2:\u001b[0m"))
                movies = search_movies_by_keyword(keyword, option)
                save_search_query(f"keyword:{keyword}")
                print_movies(movies)
            except ValueError:
                print("\u001b[31;1m Invalid input. Please enter 1 or 2. \u001b[0m")
                option = int(input("\t\u001b[33m Enter 1 or 2:\u001b[0m"))
                movies = search_movies_by_keyword(keyword, option)
                save_search_query(f"keyword:{keyword}")
                print_movies(movies)

        elif choice == "2":
            choose_year()
            year = input("\t\u001b[33m Enter year: \u001b[0m")
            print("Select an option:")
            print("1. Top-5 Rated Movies")
            print("2. Randomly Selected Movies")
            try:
                option = int(input("\t\u001b[33m Enter 1 or 2: \u001b[0m"))
                movies = search_movies_by_year(year, option)
                save_search_query(f"year:{year}")
                print_movies(movies)
            except ValueError:
                print("\u001b[31;1m Invalid input. Please enter 1 or 2. \u001b[0m")
                option = int(input("\t\u001b[33m Enter 1 or 2: \u001b[0m"))
                movies = search_movies_by_year(year, option)
                save_search_query(f"year:{year}")
                print_movies(movies)

        elif choice == "3":
            choose_genre()
            genre = input("\t\u001b[33m Enter genre: \u001b[0m")
            print("Select an option:")
            print("1. Top-5 Rated Movies")
            print("2. Randomly Selected Movies")
            try:
                option = int(input("\t\u001b[33m Enter 1 or 2: \u001b[0m"))
                movies = search_movies_by_genre(genre, option)
                save_search_query(f"genre:{genre}")
                print_movies(movies)
            except ValueError:
                print("\u001b[31;1m Invalid input. Please enter 1 or 2. \u001b[0m")
                option = int(input("\t\u001b[33m Enter 1 or 2: \u001b[0m"))
                movies = search_movies_by_genre(genre, option)
                save_search_query(f"genre:{genre}")
                print_movies(movies)

        elif choice == "4":
            choose_year()
            year = input("\t\u001b[33m Enter year: \u001b[0m")
            choose_genre()
            genre = input("\t\u001b[33m Enter genre: \u001b[0m")
            print("Select an option:")
            print("1. Top-5 Rated Movies")
            print("2. Randomly Selected Movies")
            try:
                option = int(input("\t\u001b[33m Enter 1 or 2: \u001b[0m"))
                movies = search_movies_by_year_and_genre(year, genre, option)
                save_search_query(f"year:{year}, genre:{genre}")
                print_movies(movies)
            except ValueError:
                print("\u001b[31;1m Invalid input. Please enter 1 or 2. \u001b[0m")
                option = int(input("\t\u001b[33m Enter 1 or 2: \u001b[0m"))
                movies = search_movies_by_year_and_genre(year, genre, option)
                save_search_query(f"year:{year}, genre:{genre}")
                print_movies(movies)

        elif choice == "5":
            queries = get_popular_queries()
            print("\n\t\t\u001b[35;1m Most Popular Queries:\u001b[0m")
            for query in queries:
                print(f"\u001b[35m Query: \u001b[0m {query['query']} \u001b[35m Count: \u001b[0m {query['count']}")

        elif choice == "6":
            print("\t\t\t\u001b[32;1m  Goodbye! \u001b[0m")
            break

        else:
            print("\u001b[31;1m Invalid choice. Enter from 1 to 6. Please try again. \u001b[0m")

def print_movies(movies):
    if not movies:
        print("\u001b[31;1m No movies found. \n Change the query and try again \u001b[0m")
        return
    print("*\t"*3)
    print("\u001b[35;1m MOVIES: \u001b[0m")
    print("*\t"*3)
    for movie in movies:
        print(f"\u001b[35m🎥Title:  \u001b[0m {movie['title']} "
              f"\n\u001b[35m📅Year:   \u001b[0m {movie['year']} "
              f"\n\u001b[35m🎭Genres: \u001b[0m {movie['genres']} "
              f"\n\u001b[35m👤Casts:  \u001b[0m {movie['cast']} "
              f"\n\u001b[35m⭐Rating: \u001b[0m {movie['imdb.rating']} "
              f"\n\u001b[35m📖Plot:   \u001b[0m {movie['plot']}")
        print("*\t" * 30)
if __name__ == "__main__":
    main()
