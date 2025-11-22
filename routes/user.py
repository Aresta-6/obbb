from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app
from datetime import datetime, timedelta
from utils import get_db_cursor
import mysql.connector

user_bp = Blueprint('user', __name__)

@user_bp.route('/book/<int:book_id>/reserve', methods=['POST'])
def reserve_book(book_id):
    if 'user_id' not in session:
        flash('You must be logged in to reserve a book.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if the user already has a pending reservation for this book
            cursor.execute("SELECT ReservationID FROM Reservations WHERE BookID = %s AND UserID = %s AND Status = 'Pending'", (book_id, user_id))
            if cursor.fetchone():
                flash('You already have a pending reservation for this book.', 'warning')
                return redirect(url_for('main.book_details', book_id=book_id))

            # Check if there are any available copies
            cursor.execute("SELECT COUNT(*) AS available_count FROM BookCopies WHERE BookID = %s AND Status = 'Available'", (book_id,))
            if cursor.fetchone()['available_count'] > 0:
                flash('This book is currently available for borrowing. You do not need to reserve it.', 'info')
                return redirect(url_for('main.book_details', book_id=book_id))

            # Create the reservation
            cursor.execute("INSERT INTO Reservations (BookID, UserID, ReservationDate) VALUES (%s, %s, %s)", (book_id, user_id, datetime.now()))
            flash('You have successfully reserved this book. You will be notified when it becomes available.', 'success')

    except mysql.connector.Error as err:
        flash(f'An error occurred while placing the reservation: {err}', 'danger')

    return redirect(url_for('main.book_details', book_id=book_id))


@user_bp.route('/borrow/<string:copy_id>')
def borrow(copy_id):
    if 'user_id' not in session:
        flash('You need to be logged in to borrow books.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    book_id_for_redirect = None

    try:
        with get_db_cursor(commit=True) as cursor:
            # Get BookID for redirection and check copy status
            cursor.execute("SELECT BookID, Status FROM BookCopies WHERE CopyID = %s", (copy_id,))
            copy = cursor.fetchone()
            
            if not copy:
                flash('This book copy does not exist.', 'danger')
                return redirect(url_for('main.books'))

            book_id_for_redirect = copy['BookID']

            if copy['Status'] != 'Available':
                flash('This book copy is not available for borrowing.', 'warning')
                return redirect(url_for('main.book_details', book_id=book_id_for_redirect))

            # Check user's borrow limit
            cursor.execute("SELECT MaxBorrowLimit, UserID FROM Users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                 flash('Could not find user information.', 'danger')
                 return redirect(url_for('main.book_details', book_id=book_id_for_redirect))

            limit = user['MaxBorrowLimit']
            
            cursor.execute("SELECT COUNT(*) AS current_borrows FROM BorrowingRecords WHERE UserID = %s AND ReturnDate IS NULL", (user_id,))
            current_borrows = cursor.fetchone()['current_borrows']
            
            if current_borrows >= limit:
                flash('You have reached your borrowing limit.', 'warning')
                return redirect(url_for('main.book_details', book_id=book_id_for_redirect))

            # Proceed with borrowing
            due_date = datetime.now() + timedelta(days=30)
            insert_query = "INSERT INTO BorrowingRecords (CopyID, UserID, BorrowDate, DueDate) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (copy_id, user_id, datetime.now(), due_date))
            
            update_query = "UPDATE BookCopies SET Status = 'OnLoan' WHERE CopyID = %s"
            cursor.execute(update_query, (copy_id,))
            
            flash('Book borrowed successfully!', 'success')
            
    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')
    
    if book_id_for_redirect:
        return redirect(url_for('main.book_details', book_id=book_id_for_redirect))
    else:
        return redirect(request.referrer or url_for('main.books'))


@user_bp.route('/my_borrows')
def my_borrows():
    if 'user_id' not in session:
        flash('You need to be logged in to view your borrowed books.')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    borrows = []
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT
                    br.RecordID,
                    b.Title,
                    br.BorrowDate,
                    br.DueDate,
                    bc.CopyID
                FROM
                    BorrowingRecords br
                JOIN
                    BookCopies bc ON br.CopyID = bc.CopyID
                JOIN
                    Books b ON bc.BookID = b.BookID
                WHERE
                    br.UserID = %s AND br.ReturnDate IS NULL;
            """
            cursor.execute(query, (user_id,))
            borrows = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('main.index'))

    return render_template('my_borrows.html', borrows=borrows)


@user_bp.route('/my_reservations')
def my_reservations():
    if 'user_id' not in session:
        flash('You need to be logged in to view your reservations.')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    reservations = []
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT
                    r.ReservationID,
                    b.Title,
                    r.ReservationDate,
                    r.Status
                FROM
                    Reservations r
                JOIN
                    Books b ON r.BookID = b.BookID
                WHERE
                    r.UserID = %s
                ORDER BY
                    r.ReservationDate DESC;
            """
            cursor.execute(query, (user_id,))
            reservations = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('main.index'))

    return render_template('my_reservations.html', reservations=reservations)


@user_bp.route('/reservations/cancel/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    if 'user_id' not in session:
        flash('You must be logged in to cancel a reservation.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        with get_db_cursor(commit=True) as cursor:
            # Ensure the user owns the reservation
            cursor.execute("SELECT UserID FROM Reservations WHERE ReservationID = %s", (reservation_id,))
            result = cursor.fetchone()
            if not result or result['UserID'] != user_id:
                flash('You do not have permission to cancel this reservation.', 'danger')
                return redirect(url_for('user.my_reservations'))

            # Cancel the reservation
            cursor.execute("UPDATE Reservations SET Status = 'Cancelled' WHERE ReservationID = %s", (reservation_id,))
            flash('Your reservation has been cancelled.', 'success')

    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')

    return redirect(url_for('user.my_reservations'))


@user_bp.route('/return/<int:record_id>')
def return_book(record_id):
    if 'user_id' not in session:
        flash('You need to be logged in to return books.')
        return redirect(url_for('auth.login'))

    try:
        with get_db_cursor(commit=True) as cursor:
            # Get record information, including the due date
            cursor.execute("SELECT bc.CopyID, bc.BookID, br.DueDate FROM BorrowingRecords br JOIN BookCopies bc ON br.CopyID = bc.CopyID WHERE br.RecordID = %s", (record_id,))
            record = cursor.fetchone()
            
            if not record:
                flash('Invalid record.')
                return redirect(url_for('user.my_borrows'))
                
            copy_id = record['CopyID']
            book_id = record['BookID']

            return_date = datetime.now()
            due_date = record['DueDate']
            
            # === Fine calculation logic ===
            fine_amount = 0.0
            if return_date > due_date:
                overdue_days = (return_date - due_date).days
                fine_amount = overdue_days * current_app.config['DAILY_FINE']
                flash(f'Book returned overdue. Fine incurred: {fine_amount:.2f}', 'warning')
            else:
                flash('Book returned successfully!', 'success')

            # Update the borrowing record with return date and fine amount
            cursor.execute("UPDATE BorrowingRecords SET ReturnDate = %s, Fine = %s WHERE RecordID = %s", 
                           (return_date, fine_amount, record_id))
            
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
                
                # We could also notify the user who made the reservation here
                flash('Book returned and is now reserved for the next user in the queue.', 'success')
            else:
                # No pending reservations, so mark the copy as 'Available'
                update_copy_query = "UPDATE BookCopies SET Status = 'Available' WHERE CopyID = %s"
                cursor.execute(update_copy_query, (copy_id,))
            
    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')
        
    return redirect(url_for('user.my_borrows'))

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('You need to be logged in to view your profile.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    if request.method == 'POST':
        full_name = request.form['fullname']
        
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("UPDATE Users SET FullName = %s WHERE UserID = %s", (full_name, user_id))
                session['user_name'] = full_name
                flash('Your profile has been updated successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'An error occurred while updating your profile: {err}', 'danger')
        
        return redirect(url_for('user.profile'))

    # GET request
    user = None
    history = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            
            history_query = """
                SELECT
                    b.Title,
                    br.BorrowDate,
                    br.ReturnDate,
                    br.Fine
                FROM
                    BorrowingRecords br
                JOIN
                    BookCopies bc ON br.CopyID = bc.CopyID
                JOIN
                    Books b ON bc.BookID = b.BookID
                WHERE
                    br.UserID = %s
                ORDER BY
                    br.BorrowDate DESC;
            """
            cursor.execute(history_query, (user_id,))
            history = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Database connection failed: {err}', 'danger')
        return redirect(url_for('main.index'))

    return render_template('profile.html', user=user, history=history)

@user_bp.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('You must be logged in to view notifications.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    notifications = []
    try:
        with get_db_cursor(commit=True) as cursor:
            # Fetch all notifications for the user
            cursor.execute("SELECT * FROM Notifications WHERE UserID = %s ORDER BY Timestamp DESC", (user_id,))
            notifications = cursor.fetchall()
            
            # Mark all unread notifications as read
            cursor.execute("UPDATE Notifications SET IsRead = TRUE WHERE UserID = %s AND IsRead = FALSE", (user_id,))

    except mysql.connector.Error as err:
        flash(f'An error occurred: {err}', 'danger')
            
    return render_template('notifications.html', notifications=notifications)


