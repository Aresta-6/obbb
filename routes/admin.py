from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from utils import get_db_cursor, admin_required
import mysql.connector

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    borrows = []
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT
                    br.RecordID,
                    b.Title,
                    u.FullName,
                    u.UserID,
                    br.BorrowDate,
                    br.DueDate
                FROM
                    BorrowingRecords br
                JOIN
                    BookCopies bc ON br.CopyID = bc.CopyID
                JOIN
                    Books b ON bc.BookID = b.BookID
                JOIN
                    Users u ON br.UserID = u.UserID
                WHERE
                    br.ReturnDate IS NULL
                ORDER BY
                    br.DueDate ASC;
            """
            cursor.execute(query)
            borrows = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return render_template('admin/dashboard.html', borrows=borrows)
    
    return render_template('admin/dashboard.html', borrows=borrows, today=datetime.now().date())


@admin_bp.route('/books')
@admin_required
def manage_books():
    books = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM Books ORDER BY Title;")
            books = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/manage_books.html', books=books)


@admin_bp.route('/books/manage_copies/<int:book_id>', methods=['GET'])
@admin_required
def manage_copies(book_id):
    book = None
    copies = []
    try:
        with get_db_cursor() as cursor:
            # Fetch book details
            cursor.execute("SELECT BookID, Title FROM Books WHERE BookID = %s", (book_id,))
            book = cursor.fetchone()
            if not book:
                flash('Book not found.', 'danger')
                return redirect(url_for('admin.manage_books'))

            # Fetch copies for the book
            cursor.execute("SELECT * FROM BookCopies WHERE BookID = %s ORDER BY CopyID", (book_id,))
            copies = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('admin.manage_books'))
    
    return render_template('admin/manage_copies.html', book=book, copies=copies)


@admin_bp.route('/books/add_copy/<int:book_id>', methods=['POST'])
@admin_required
def add_copy(book_id):
    copy_id = request.form.get('copy_id')
    location = request.form.get('location')

    if not copy_id:
        flash('Copy ID is required.', 'danger')
        return redirect(url_for('admin.manage_copies', book_id=book_id))

    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if copy ID already exists
            cursor.execute("SELECT 1 FROM BookCopies WHERE CopyID = %s", (copy_id,))
            if cursor.fetchone():
                flash('A copy with this ID already exists.', 'danger')
                return redirect(url_for('admin.manage_copies', book_id=book_id))

            # Insert new copy
            cursor.execute("INSERT INTO BookCopies (CopyID, BookID, Location, EntryDate) VALUES (%s, %s, %s, %s)",
                           (copy_id, book_id, location, datetime.now()))
            flash('New copy added successfully.', 'success')

    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')

    return redirect(url_for('admin.manage_copies', book_id=book_id))


@admin_bp.route('/books/delete_copy/<string:copy_id>', methods=['POST'])
@admin_required
def delete_copy(copy_id):
    book_id = None
    try:
        with get_db_cursor(commit=True) as cursor:
            # Get BookID for redirection and check status
            cursor.execute("SELECT BookID, Status FROM BookCopies WHERE CopyID = %s", (copy_id,))
            copy = cursor.fetchone()

            if not copy:
                flash('Copy not found.', 'danger')
                return redirect(url_for('admin.manage_books'))
            
            book_id = copy['BookID']

            if copy['Status'] != 'Available':
                flash('Cannot delete a copy that is not available (e.g., on loan or reserved).', 'danger')
                return redirect(url_for('admin.manage_copies', book_id=book_id))

            # Delete the copy
            cursor.execute("DELETE FROM BookCopies WHERE CopyID = %s", (copy_id,))
            flash('Copy deleted successfully.', 'success')

    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')

    if book_id:
        return redirect(url_for('admin.manage_copies', book_id=book_id))
    return redirect(url_for('admin.manage_books'))


@admin_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    if request.method == 'POST':
        try:
            with get_db_cursor(commit=True) as cursor:
                # Get form data
                title = request.form['title']
                isbn = request.form['isbn']
                publisher_id = request.form['publisher']
                category_id = request.form['category']
                publication_date = request.form.get('publication_date') or None
                description = request.form.get('description')
                author_names = [name.strip() for name in request.form['authors'].split(',')]
                cover_image_url = request.form.get('cover_image_url')

                # 1. Update Books table
                book_query = """
                    UPDATE Books SET Title=%s, ISBN=%s, PublisherID=%s, CategoryID=%s, 
                    PublicationDate=%s, Description=%s, CoverImageURL=%s WHERE BookID=%s
                """
                cursor.execute(book_query, (title, isbn, publisher_id, category_id, publication_date, description, cover_image_url, book_id))

                # 2. Update Authors (delete old and insert new)
                cursor.execute("DELETE FROM Book_Authors WHERE BookID = %s", (book_id,))
                
                for name in author_names:
                    if not name: continue
                    cursor.execute("SELECT AuthorID FROM Authors WHERE AuthorName = %s", (name,))
                    author_result = cursor.fetchone()
                    
                    if author_result:
                        author_id = author_result['AuthorID']
                    else:
                        cursor.execute("INSERT INTO Authors (AuthorName) VALUES (%s)", (name,))
                        author_id = cursor.lastrowid
                    
                    cursor.execute("INSERT INTO Book_Authors (BookID, AuthorID) VALUES (%s, %s)", (book_id, author_id))

                flash('Book updated successfully!', 'success')

        except mysql.connector.Error as err:
            flash(f'An error occurred: {err}', 'danger')

        return redirect(url_for('admin.manage_books'))

    # GET request
    book = None
    categories = []
    publishers = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM Books WHERE BookID = %s", (book_id,))
            book = cursor.fetchone()

            # Fetch the book's authors
            cursor.execute("""
                SELECT GROUP_CONCAT(a.AuthorName SEPARATOR ', ') AS authors
                FROM Book_Authors ba
                JOIN Authors a ON ba.AuthorID = a.AuthorID
                WHERE ba.BookID = %s
            """, (book_id,))
            authors = cursor.fetchone()
            book['authors'] = authors['authors'] if authors else ''

            # Fetch all categories and publishers for dropdowns
            cursor.execute("SELECT * FROM Categories ORDER BY CategoryName;")
            categories = cursor.fetchall()
            cursor.execute("SELECT * FROM Publishers ORDER BY PublisherName;")
            publishers = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('admin.manage_books'))

    return render_template('admin/edit_book.html', book=book, categories=categories, publishers=publishers)


@admin_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if any copies are on loan
            cursor.execute("""
                SELECT COUNT(*) AS on_loan_count 
                FROM BookCopies 
                WHERE BookID = %s AND Status = 'OnLoan'
            """, (book_id,))
            on_loan_count = cursor.fetchone()['on_loan_count']

            if on_loan_count > 0:
                flash('Cannot delete this book because one or more copies are currently on loan.', 'danger')
                return redirect(url_for('admin.manage_books'))

            # Check for pending reservations
            cursor.execute("SELECT COUNT(*) AS reservation_count FROM Reservations WHERE BookID = %s AND Status = 'Pending'", (book_id,))
            reservation_count = cursor.fetchone()['reservation_count']

            if reservation_count > 0:
                flash('Cannot delete this book because there are pending reservations.', 'danger')
                return redirect(url_for('admin.manage_books'))

            # Proceed with deletion in the correct order
            cursor.execute("DELETE FROM Reservations WHERE BookID = %s", (book_id,))
            cursor.execute("DELETE FROM Book_Authors WHERE BookID = %s", (book_id,))
            
            # Get copy IDs to delete from borrowing records
            cursor.execute("SELECT CopyID FROM BookCopies WHERE BookID = %s", (book_id,))
            copy_ids = [row['CopyID'] for row in cursor.fetchall()]
            if copy_ids:
                format_strings = ','.join(['%s'] * len(copy_ids))
                cursor.execute(f"DELETE FROM BorrowingRecords WHERE CopyID IN ({format_strings})", tuple(copy_ids))

            cursor.execute("DELETE FROM BookCopies WHERE BookID = %s", (book_id,))
            cursor.execute("DELETE FROM Books WHERE BookID = %s", (book_id,))

            flash('Book deleted successfully.', 'success')

    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')

    return redirect(url_for('admin.manage_books'))


@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        try:
            with get_db_cursor(commit=True) as cursor:
                # Get form data
                title = request.form['title']
                isbn = request.form['isbn']
                publisher_id = request.form['publisher']
                category_id = request.form['category']
                publication_date = request.form.get('publication_date') or None
                description = request.form.get('description')
                author_names = [name.strip() for name in request.form['authors'].split(',')]
                cover_image_url = request.form.get('cover_image_url')

                # 1. Insert into Books table
                book_query = """
                    INSERT INTO Books (Title, ISBN, PublisherID, CategoryID, PublicationDate, Description, CoverImageURL)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(book_query, (title, isbn, publisher_id, category_id, publication_date, description, cover_image_url))
                book_id = cursor.lastrowid

                # 2. Handle Authors
                for name in author_names:
                    if not name: continue
                    # Check if author exists
                    cursor.execute("SELECT AuthorID FROM Authors WHERE AuthorName = %s", (name,))
                    author_result = cursor.fetchone()
                    
                    if author_result:
                        author_id = author_result[0]
                    else:
                        # Insert new author
                        cursor.execute("INSERT INTO Authors (AuthorName) VALUES (%s)", (name,))
                        author_id = cursor.lastrowid
                    
                    # 3. Link in Book_Authors
                    cursor.execute("INSERT INTO Book_Authors (BookID, AuthorID) VALUES (%s, %s)", (book_id, author_id))

                flash('Book added successfully!', 'success')

        except mysql.connector.Error as err:
            flash(f'An error occurred: {err}', 'danger')

        return redirect(url_for('admin.manage_books'))

    # GET request
    categories = []
    publishers = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM Categories ORDER BY CategoryName;")
            categories = cursor.fetchall()
            cursor.execute("SELECT * FROM Publishers ORDER BY PublisherName;")
            publishers = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('admin.manage_books'))

    return render_template('admin/add_book.html', categories=categories, publishers=publishers)


@admin_bp.route('/reservations')
@admin_required
def reservations():
    reservations = []
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT
                    r.ReservationID,
                    b.Title,
                    u.FullName,
                    u.UserID,
                    r.ReservationDate,
                    r.Status
                FROM
                    Reservations r
                JOIN
                    Books b ON r.BookID = b.BookID
                JOIN
                    Users u ON r.UserID = u.UserID
                ORDER BY
                    r.ReservationDate DESC;
            """
            cursor.execute(query)
            reservations = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/manage_reservations.html', reservations=reservations)


@admin_bp.route('/reservations/cancel/<int:reservation_id>', methods=['POST'])
@admin_required
def cancel_reservation(reservation_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE Reservations SET Status = 'Cancelled' WHERE ReservationID = %s", (reservation_id,))
            flash('Reservation cancelled successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')
    return redirect(url_for('admin.reservations'))

@admin_bp.route('/reservations/fulfill/<int:reservation_id>', methods=['POST'])
@admin_required
def fulfill_reservation(reservation_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            # Get reservation details
            cursor.execute("SELECT BookID, UserID FROM Reservations WHERE ReservationID = %s", (reservation_id,))
            reservation = cursor.fetchone()
            if not reservation:
                flash('Reservation not found.', 'danger')
                return redirect(url_for('admin.reservations'))
            
            book_id = reservation['BookID']
            user_id = reservation['UserID']

            # Find an available copy for the book
            cursor.execute("SELECT CopyID FROM BookCopies WHERE BookID = %s AND Status = 'Available' LIMIT 1", (book_id,))
            available_copy = cursor.fetchone()

            if not available_copy:
                flash('No available copies to fulfill this reservation.', 'danger')
                return redirect(url_for('admin.reservations'))

            copy_id = available_copy['CopyID']

            
            # Update reservation status to Fulfilled
            cursor.execute("UPDATE Reservations SET Status = 'Fulfilled' WHERE ReservationID = %s", (reservation_id,))
            
            # Update book copy status to OnLoan and create a borrowing record
            due_date = datetime.now() + timedelta(days=30)
            cursor.execute("UPDATE BookCopies SET Status = 'OnLoan' WHERE CopyID = %s", (copy_id,))
            cursor.execute("INSERT INTO BorrowingRecords (CopyID, UserID, BorrowDate, DueDate) VALUES (%s, %s, %s, %s)", (copy_id, user_id, datetime.now(), due_date))
            
            flash('Reservation fulfilled and book borrowed successfully.', 'success')

    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')
    return redirect(url_for('admin.reservations'))


@admin_bp.route('/remind/<int:record_id>', methods=['POST'])
@admin_required
def remind_user(record_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            # Get user, book, and due date info from the borrow record
            query = """
                SELECT u.FullName, u.UserID, b.Title, br.DueDate
                FROM BorrowingRecords br
                JOIN Users u ON br.UserID = u.UserID
                JOIN BookCopies bc ON br.CopyID = bc.CopyID
                JOIN Books b ON bc.BookID = b.BookID
                WHERE br.RecordID = %s
            """
            cursor.execute(query, (record_id,))
            record_info = cursor.fetchone()

            if record_info:
                user_id = record_info['UserID']
                user_name = record_info['FullName']
                book_title = record_info['Title']
                due_date = record_info['DueDate']
                
                today = datetime.now().date()
                due_date_str = due_date.strftime('%Y-%m-%d')
                
                # Determine the correct message
                if due_date < today:
                    message = f"Overdue Reminder: The book '{book_title}' was due on {due_date_str}. Please return it as soon as possible."
                elif (due_date - today).days <= 3:
                    message = f"Due Soon Reminder: The book '{book_title}' is due on {due_date_str}. Please remember to return it on time."
                else:
                    message = f"Book Reminder: This is a friendly reminder for the book '{book_title}', which is due on {due_date_str}."

                # Insert the notification for the user
                insert_query = "INSERT INTO Notifications (UserID, Message) VALUES (%s, %s)"
                cursor.execute(insert_query, (user_id, message))

                # Flash a confirmation for the admin
                flash(f"A reminder has been sent to {user_name} ({user_id}).", 'success')
            else:
                flash('Could not find the borrowing record to send a reminder.', 'danger')

    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/manage_returns')
@admin_required
def manage_returns():
    borrows = []
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT
                    br.RecordID,
                    b.Title,
                    u.FullName,
                    u.UserID,
                    br.BorrowDate,
                    br.DueDate,
                    br.ReturnDate
                FROM
                    BorrowingRecords br
                JOIN
                    BookCopies bc ON br.CopyID = bc.CopyID
                JOIN
                    Books b ON bc.BookID = b.BookID
                JOIN
                    Users u ON br.UserID = u.UserID
                ORDER BY
                    br.BorrowDate DESC;
            """
            cursor.execute(query)
            borrows = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/manage_returns.html', borrows=borrows)


@admin_bp.route('/force_return/<int:record_id>', methods=['POST'])
@admin_required
def force_return(record_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            # Get CopyID and BookID from the record
            cursor.execute("""
                SELECT bc.CopyID, bc.BookID 
                FROM BorrowingRecords br
                JOIN BookCopies bc ON br.CopyID = bc.CopyID
                WHERE br.RecordID = %s
            """, (record_id,))
            record = cursor.fetchone()
            
            if not record:
                flash('Invalid record.', 'danger')
                return redirect(url_for('admin.manage_returns'))
                
            copy_id = record['CopyID']
            book_id = record['BookID']

            # Update the borrowing record
            cursor.execute("UPDATE BorrowingRecords SET ReturnDate = %s WHERE RecordID = %s", (datetime.now(), record_id))
            
            # Check for pending reservations for this book
            cursor.execute("""
                SELECT ReservationID, UserID 
                FROM Reservations 
                WHERE BookID = %s AND Status = 'Pending' 
                ORDER BY ReservationDate ASC 
                LIMIT 1
            """, (book_id,))
            reservation = cursor.fetchone()
            
            if reservation:
                # A reservation exists, so mark the copy as 'Reserved'
                update_copy_query = "UPDATE BookCopies SET Status = 'Reserved' WHERE CopyID = %s"
                cursor.execute(update_copy_query, (copy_id,))
                
                # Update the reservation status to 'Fulfilled'
                reservation_id = reservation['ReservationID']
                cursor.execute("UPDATE Reservations SET Status = 'Fulfilled' WHERE ReservationID = %s", (reservation_id,))
                flash('Book returned and is now reserved for the next user in the queue.', 'success')
            else:
                # No pending reservations, so mark the copy as 'Available'
                update_copy_query = "UPDATE BookCopies SET Status = 'Available' WHERE CopyID = %s"
                cursor.execute(update_copy_query, (copy_id,))
                flash('Book returned successfully.', 'success')
        
    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')
        
    return redirect(url_for('admin.manage_returns'))


