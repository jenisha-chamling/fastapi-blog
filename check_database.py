
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "blog.db"


def print_section(title):
    print(f"\n{'=' * 55}")
    print(title)
    print("=" * 55)


def display_query(cursor, query, parameters=()):
    cursor.execute(query, parameters)
    rows = cursor.fetchall()

    if not rows:
        print("No records found.")
        return

    for row in rows:
        print(dict(row))


def main():
    if not DATABASE_PATH.exists():
        print(f"Database not found: {DATABASE_PATH}")
        return

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        # 1. Inspect database tables
        print_section("1. DATABASE TABLES")
        display_query(
            cursor,
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        )

        # 2. Inspect the posts table structure
        print_section("2. POSTS TABLE STRUCTURE")
        display_query(cursor, "PRAGMA table_info(posts)")

        # 3. Retrieve all posts
        print_section("3. ALL POSTS")
        display_query(
            cursor,
            """
            SELECT id, author, title, content, date_posted
            FROM posts
            ORDER BY id DESC
            """
        )

        # 4. Count all posts
        print_section("4. TOTAL POSTS")
        display_query(
            cursor,
            "SELECT COUNT(*) AS total_posts FROM posts"
        )

        # 5. Find a post by ID
        print_section("5. FIND POST BY ID")
        display_query(
            cursor,
            """
            SELECT *
            FROM posts
            WHERE id = ?
            """,
            (1,)
        )

        # 6. Find posts by author
        print_section("6. POSTS BY JENISHA")
        display_query(
            cursor,
            """
            SELECT id, title, date_posted
            FROM posts
            WHERE author = ?
            ORDER BY id DESC
            """,
            ("Jenisha",)
        )

        # 7. Search titles using a keyword
        print_section("7. SEARCH TITLES")
        display_query(
            cursor,
            """
            SELECT id, author, title
            FROM posts
            WHERE title LIKE ?
            ORDER BY id DESC
            """,
            ("%Python%",)
        )

        # 8. Find posts containing a keyword in their content
        print_section("8. SEARCH POST CONTENT")
        display_query(
            cursor,
            """
            SELECT id, title
            FROM posts
            WHERE content LIKE ?
            ORDER BY id DESC
            """,
            ("%FastAPI%",)
        )

        # 9. Retrieve the latest five posts
        print_section("9. LATEST FIVE POSTS")
        display_query(
            cursor,
            """
            SELECT id, author, title, date_posted
            FROM posts
            ORDER BY id DESC
            LIMIT ?
            """,
            (5,)
        )

        # 10. Count posts written by each author
        print_section("10. POSTS PER AUTHOR")
        display_query(
            cursor,
            """
            SELECT author, COUNT(*) AS total_posts
            FROM posts
            GROUP BY author
            ORDER BY total_posts DESC, author ASC
            """
        )

        # 11. Find posts with blank or missing text
        print_section("11. CHECK EMPTY FIELDS")
        display_query(
            cursor,
            """
            SELECT id, author, title
            FROM posts
            WHERE author IS NULL OR TRIM(author) = ''
               OR title IS NULL OR TRIM(title) = ''
               OR content IS NULL OR TRIM(content) = ''
               OR date_posted IS NULL OR TRIM(date_posted) = ''
            """
        )

        # 12. Find duplicate titles (case-insensitive)
        print_section("12. CHECK DUPLICATE TITLES")
        display_query(
            cursor,
            """
            SELECT LOWER(TRIM(title)) AS normalized_title,
                   COUNT(*) AS occurrences
            FROM posts
            GROUP BY LOWER(TRIM(title))
            HAVING COUNT(*) > 1
            ORDER BY occurrences DESC
            """
        )

        # 13. Find duplicate post IDs
        print_section("13. CHECK DUPLICATE IDS")
        display_query(
            cursor,
            """
            SELECT id, COUNT(*) AS occurrences
            FROM posts
            GROUP BY id
            HAVING COUNT(*) > 1
            """
        )

        # 14. Check the longest title
        print_section("14. LONGEST TITLE")
        display_query(
            cursor,
            """
            SELECT id, title, LENGTH(title) AS title_length
            FROM posts
            ORDER BY LENGTH(title) DESC
            LIMIT 1
            """
        )

        # 15. Find posts with titles longer than the app's limit
        print_section("15. TITLES OVER 160 CHARACTERS")
        display_query(
            cursor,
            """
            SELECT id, LENGTH(title) AS title_length, title
            FROM posts
            WHERE LENGTH(title) > 160
            """
        )

        # 16. Check the number of posts with empty content
        print_section("16. EMPTY CONTENT COUNT")
        display_query(
            cursor,
            """
            SELECT COUNT(*) AS empty_content_count
            FROM posts
            WHERE content IS NULL OR TRIM(content) = ''
            """
        )

        # 17. Find the smallest and largest post IDs
        print_section("17. POST ID RANGE")
        display_query(
            cursor,
            """
            SELECT MIN(id) AS smallest_id,
                   MAX(id) AS largest_id,
                   COUNT(*) AS total_posts
            FROM posts
            """
        )

        # 18. Verify the table's primary-key definition
        print_section("18. PRIMARY KEY INFORMATION")
        display_query(cursor, "PRAGMA table_info(posts)")

        print_section("DATABASE CHECKS COMPLETED")
        print("All checks finished. No records were modified.")

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
