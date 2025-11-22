-- Drop tables in reverse order of dependency to avoid foreign key constraints
DROP TABLE IF EXISTS SystemLogs;
DROP TABLE IF EXISTS Notifications;
DROP TABLE IF EXISTS BorrowingRecords;
DROP TABLE IF EXISTS Reservations;
DROP TABLE IF EXISTS BookCopies;
DROP TABLE IF EXISTS Book_Authors;
DROP TABLE IF EXISTS Authors;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Publishers;
DROP TABLE IF EXISTS Users;

-- Create Users table
CREATE TABLE Users (
    UserID VARCHAR(50) PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    UserType ENUM('Student', 'Teacher') NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    MaxBorrowLimit INT DEFAULT 10
);

-- Create Publishers table
CREATE TABLE Publishers (
    PublisherID INT AUTO_INCREMENT PRIMARY KEY,
    PublisherName VARCHAR(255) NOT NULL UNIQUE
);

-- Create Categories table
CREATE TABLE Categories (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    CategoryName VARCHAR(255) NOT NULL UNIQUE
);

-- Create Books table
CREATE TABLE Books (
    BookID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    ISBN VARCHAR(20) UNIQUE,
    PublisherID INT,
    CategoryID INT,
    PublicationDate DATE,
    Description TEXT,
    CoverImageURL VARCHAR(255),
    FOREIGN KEY (PublisherID) REFERENCES Publishers(PublisherID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- Create Authors table
CREATE TABLE Authors (
    AuthorID INT AUTO_INCREMENT PRIMARY KEY,
    AuthorName VARCHAR(255) NOT NULL UNIQUE
);

-- Create Book_Authors linking table
CREATE TABLE Book_Authors (
    BookID INT,
    AuthorID INT,
    PRIMARY KEY (BookID, AuthorID),
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE,
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID) ON DELETE CASCADE
);

-- Create BookCopies table
CREATE TABLE BookCopies (
    CopyID VARCHAR(50) PRIMARY KEY,
    BookID INT,
    Status ENUM('Available', 'OnLoan', 'Reserved', 'Lost') DEFAULT 'Available',
    Location VARCHAR(255),
    EntryDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE
);

-- Create Reservations table
CREATE TABLE Reservations (
    ReservationID INT AUTO_INCREMENT PRIMARY KEY,
    BookID INT,
    UserID VARCHAR(50),
    ReservationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Status ENUM('Pending', 'Fulfilled', 'Cancelled') DEFAULT 'Pending',
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

-- Create BorrowingRecords table
CREATE TABLE BorrowingRecords (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    CopyID VARCHAR(50),
    UserID VARCHAR(50),
    BorrowDate DATETIME NOT NULL,
    DueDate DATETIME NOT NULL,
    ReturnDate DATETIME,
    Fine DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (CopyID) REFERENCES BookCopies(CopyID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

-- Create Notifications table
CREATE TABLE Notifications (
    NotificationID INT AUTO_INCREMENT PRIMARY KEY,
    UserID VARCHAR(50),
    Message TEXT NOT NULL,
    IsRead BOOLEAN DEFAULT FALSE,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

-- Create SystemLogs table for admin actions
CREATE TABLE SystemLogs (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    AdminID VARCHAR(50),
    Action VARCHAR(255),
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (AdminID) REFERENCES Users(UserID)
);

-- Add indexes for performance
CREATE INDEX idx_books_title ON Books(Title);
CREATE INDEX idx_borrowing_records_user ON BorrowingRecords(UserID);
CREATE INDEX idx_reservations_user ON Reservations(UserID);
