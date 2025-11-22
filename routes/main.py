from flask import Blueprint, render_template, request, session, current_app
from utils import get_db_cursor
import mysql.connector

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/books')
def books():
    try:
        with get_db_cursor() as cursor:
            # Fetch data for filters
            cursor.execute("SELECT * FROM Categories ORDER BY CategoryName;")
            categories = cursor.fetchall()
            cursor.execute("SELECT * FROM Publishers ORDER BY PublisherName;")
            publishers = cursor.fetchall()

            search_term = request.args.get('search')
            category_filter = request.args.get('category')
            publisher_filter = request.args.get('publisher')
            
            page = request.args.get('page', 1, type=int)
            per_page = current_app.config['PER_PAGE']
            offset = (page - 1) * per_page
            
            params = []
            where_clauses = []

            if search_term:
                where_clauses.append("(b.Title LIKE %s OR a.AuthorName LIKE %s OR b.ISBN LIKE %s)")
                like_term = f"%{search_term}%"
                params.extend([like_term, like_term, like_term])
            
            if category_filter:
                where_clauses.append("b.CategoryID = %s")
                params.append(category_filter)

            if publisher_filter:
                where_clauses.append("b.PublisherID = %s")
                params.append(publisher_filter)

            # Count total books for pagination
            count_query = "SELECT COUNT(DISTINCT b.BookID) as total FROM Books b LEFT JOIN Book_Authors ba ON b.BookID = ba.BookID LEFT JOIN Authors a ON ba.AuthorID = a.AuthorID"
            if where_clauses:
                count_query += " WHERE " + " AND ".join(where_clauses)
            
            cursor.execute(count_query, params)
            total_books = cursor.fetchone()['total']
            total_pages = (total_books + per_page - 1) // per_page

            # Fetch books for the current page
            query = "SELECT b.*, GROUP_CONCAT(a.AuthorName) AS authors FROM Books b LEFT JOIN Book_Authors ba ON b.BookID = ba.BookID LEFT JOIN Authors a ON ba.AuthorID = a.AuthorID"
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " GROUP BY b.BookID ORDER BY CASE WHEN b.Title LIKE %s THEN 1 ELSE 2 END, b.Title ASC LIMIT %s OFFSET %s;"
            like_term_for_order = f"{search_term}%" if search_term else ""
            params.extend([like_term_for_order, per_page, offset])
            
            cursor.execute(query, params)
            books_data = cursor.fetchall()
            
    except mysql.connector.Error as err:
        return f"Error connecting to the database: {err}", 500
    
    return render_template('books.html', books=books_data, categories=categories, publishers=publishers, current_page=page, total_pages=total_pages)


@main_bp.route('/book/<int:book_id>')
def book_details(book_id):
    book = None
    copies = []
    user_has_reserved = False
    try:
        with get_db_cursor() as cursor:
            # Fetch book details
            book_query = """
                SELECT
                    b.BookID, b.Title, b.ISBN, p.PublisherName, c.CategoryName,
                    GROUP_CONCAT(DISTINCT a.AuthorName SEPARATOR ', ') AS Authors,
                    b.Description
                FROM Books b
                LEFT JOIN Publishers p ON b.PublisherID = p.PublisherID
                LEFT JOIN Categories c ON b.CategoryID = c.CategoryID
                LEFT JOIN Book_Authors ba ON b.BookID = ba.BookID
                LEFT JOIN Authors a ON ba.AuthorID = a.AuthorID
                WHERE b.BookID = %s
                GROUP BY b.BookID;
            """
            cursor.execute(book_query, (book_id,))
            book = cursor.fetchone()
            
            if not book:
                return "Book not found.", 404

            # Fetch book copies
            copies_query = "SELECT CopyID, Status, Location FROM BookCopies WHERE BookID = %s;"
            cursor.execute(copies_query, (book_id,))
            copies = cursor.fetchall()
            
            # Check for available copies
            available_copies = sum(1 for copy in copies if copy['Status'] == 'Available')
            
            # Check if the user has already reserved this book
            if 'user_id' in session:
                user_id = session['user_id']
                reservation_query = "SELECT 1 FROM Reservations WHERE BookID = %s AND UserID = %s AND Status = 'Pending'"
                cursor.execute(reservation_query, (book_id, user_id))
                user_has_reserved = cursor.fetchone() is not None
    except mysql.connector.Error as err:
        return f"Error connecting to the database: {err}", 500
        
    return render_template('book_details.html', book=book, copies=copies, available_copies=available_copies, user_has_reserved=user_has_reserved)


