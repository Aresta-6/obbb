-- SQL Data Population Script
-- This script clears existing data and populates the database with a realistic set of data.

SET FOREIGN_KEY_CHECKS=0;

-- Step 1: Truncate all relevant tables to start fresh
TRUNCATE TABLE BorrowingRecords;
TRUNCATE TABLE Reservations;
TRUNCATE TABLE BookCopies;
TRUNCATE TABLE Book_Authors;
TRUNCATE TABLE Books;
TRUNCATE TABLE Authors;
TRUNCATE TABLE Publishers;
TRUNCATE TABLE Categories;
TRUNCATE TABLE Users;

-- Step 2: Insert Categories
INSERT INTO `Categories` (`CategoryID`, `CategoryName`) VALUES
(1, '武侠'),
(2, '奇幻'),
(3, '小说'),
(4, '教辅'),
(5, 'Science Fiction'),
(6, 'Classic Literature'),
(7, 'History'),
(8, 'Fantasy'),
(9, 'Biography'),
(10, 'Mystery'),
(11, 'Non-Fiction'),
(12, 'Thriller'),
(13, 'Children\'s Literature'),
(14, 'Philosophy'),
(15, 'Dystopian'),
(16, 'Memoir'),
(17, 'Historical Fiction');

-- Step 3: Insert Publishers
INSERT INTO `Publishers` (`PublisherID`, `PublisherName`) VALUES
(1, '人民文学出版社'),
(2, '长江文艺出版社'),
(3, '作家出版社'),
(4, '高等教育出版社'),
(5, 'Penguin Random House'),
(6, 'HarperCollins'),
(7, 'Simon & Schuster'),
(8, 'Hachette Book Group'),
(9, 'Macmillan Publishers'),
(10, 'Scholastic'),
(11, 'Liveright'),
(12, 'Viking Press'),
(13, 'Scribner'),
(14, 'Mariner Books'),
(15, 'Bloomsbury Publishing'),
(16, 'Crossway');

-- Step 4: Insert Authors
INSERT INTO `Authors` (`AuthorID`, `AuthorName`) VALUES
(1, '金庸'),
(2, '江南'),
(3, '余华'),
(4, '王小波'),
(5, '同济大学数学系'),
(6, 'George Orwell'),
(7, 'J.K. Rowling'),
(8, 'J.R.R. Tolkien'),
(9, 'Jane Austen'),
(10, 'F. Scott Fitzgerald'),
(11, 'Harper Lee'),
(12, 'Yuval Noah Harari'),
(13, 'Tara Westover'),
(14, 'Michelle Obama'),
(15, 'Anne Frank'),
(16, 'Kristin Hannah'),
(17, 'Madeline Miller'),
(18, 'Frank Herbert'),
(19, 'Andy Weir'),
(20, 'Richard Osman'),
(21, 'Howard Zinn'),
(22, 'Mary Shelley'),
(23, 'Leo Tolstoy'),
(24, 'Virginia Evans'),
(25, 'R. F. Kuang'),
(26, 'Frank E. Peretti');


-- Step 5: Insert Users (Passwords are hashed 'password123')
INSERT INTO `Users` (`UserID`, `FullName`, `UserType`, `PasswordHash`, `RegistrationDate`, `MaxBorrowLimit`) VALUES
('admin', 'Admin User', 'Teacher', 'scrypt:32768:8:1$6ARrmQKY7ThprtR1$477f0fe06f52bfebc43f559fde7a8845a0fdfa57cd8b951edfc8ede74aa70401fd4db282250cdceabeccf708915fd0266fec9b42c2fa5aeeb698e74f6b10a6df', '2023-01-01', 20),
('student1', 'John Smith', 'Student', 'scrypt:32768:8:1$6ARrmQKY7ThprtR1$477f0fe06f52bfebc43f559fde7a8845a0fdfa57cd8b951edfc8ede74aa70401fd4db282250cdceabeccf708915fd0266fec9b42c2fa5aeeb698e74f6b10a6df', '2023-02-10', 5),
('student2', 'Emily Jones', 'Student', 'scrypt:32768:8:1$6ARrmQKY7ThprtR1$477f0fe06f52bfebc43f559fde7a8845a0fdfa57cd8b951edfc8ede74aa70401fd4db282250cdceabeccf708915fd0266fec9b42c2fa5aeeb698e74f6b10a6df', '2023-03-15', 5),
('teacher1', 'Dr. Alan Grant', 'Teacher', 'scrypt:32768:8:1$6ARrmQKY7ThprtR1$477f0fe06f52bfebc43f559fde7a8845a0fdfa57cd8b951edfc8ede74aa70401fd4db282250cdceabeccf708915fd0266fec9b42c2fa5aeeb698e74f6b10a6df', '2023-01-20', 20),
('student3', 'Sarah Miller', 'Student', 'scrypt:32768:8:1$6ARrmQKY7ThprtR1$477f0fe06f52bfebc43f559fde7a8845a0fdfa57cd8b951edfc8ede74aa70401fd4db282250cdceabeccf708915fd0266fec9b42c2fa5aeeb698e74f6b10a6df', '2023-05-01', 5),
('student4', 'David Wilson', 'Student', 'scrypt:32768:8:1$6ARrmQKY7ThprtR1$477f0fe06f52bfebc43f559fde7a8845a0fdfa57cd8b951edfc8ede74aa70401fd4db282250cdceabeccf708915fd0266fec9b42c2fa5aeeb698e74f6b10a6df', '2023-06-22', 5),
('teacher2', 'Dr. Ellie Sattler', 'Teacher', 'scrypt:32768:8:1$6ARrmQKY7ThprtR1$477f0fe06f52bfebc43f559fde7a8845a0fdfa57cd8b951edfc8ede74aa70401fd4db282250cdceabeccf708915fd0266fec9b42c2fa5aeeb698e74f6b10a6df', '2023-04-11', 20);

-- Step 6: Insert Books
INSERT INTO `Books` (`BookID`, `Title`, `ISBN`, `PublicationDate`, `PublisherID`, `CategoryID`, `Description`) VALUES
(1, '龙族I：火之晨曦', '9787535449149', '2011-04-01', 2, 2, '《龙族Ⅰ火之晨曦》是作家江南创作的系列长篇魔幻小说《龙族》的第一部，于2010年4月首次出版。'),
(2, '龙族II：悼亡者之瞳', '9787535454563', '2012-05-01', 2, 2, '《龙族Ⅱ·悼亡者之瞳》是作家江南创作的系列长篇魔幻小说《龙族》的第二部。'),
(3, '龙族III：黑月之潮', '9787535468881', '2013-12-01', 2, 2, '《龙族Ⅲ黑月之潮》是2013年长江文艺出版社出版的中篇小说，作者是江南。'),
(4, '射雕英雄传', '9787020024429', '1957-01-01', 1, 1, '《射雕英雄传》是金庸创作的长篇武侠小说，最初连载于1957年至1959年的《香港商报》，后收录于《金庸作品集》中，是金庸“射雕三部曲”的第一部。'),
(5, '神雕侠侣', '9787020024436', '1959-01-01', 1, 1, '《神雕侠侣》是金庸所著的武侠小说，作于1959年。是“射雕三部曲”系列的第二部。'),
(6, '倚天屠龙记', '9787020024443', '1961-01-01', 1, 1, '《倚天屠龙记》是作家金庸创作的长篇武侠小说，连载于1961—1962年的香港《明报》，是“射雕三部曲”系列的第三部。'),
(7, '天龙八部', '9787020024450', '1963-01-01', 1, 1, '《天龙八部》是金庸创作的长篇武侠小说，1963—1966年连载于《明报》和新加坡《南洋商报》.'),
(8, '笑傲江湖', '9787020024467', '1967-01-01', 1, 1, '《笑傲江湖》是金庸1967年开始创作的一部作品，1969年完成，属于后期的作品。'),
(9, '鹿鼎记', '9787020024474', '1969-01-01', 1, 1, '《鹿鼎记》是香港作家金庸（查良镛）的最后一部长篇武侠小说。'),
(10, '活着', '9787506365437', '1993-01-01', 3, 3, '《活着》是中国当代作家余华创作的长篇小说。'),
(11, '黄金时代', '9787536692898', '1997-01-01', 3, 3, '《黄金时代》是作家王小波创作的中篇小说。'),
(12, '高等数学', '9787040492324', '2018-01-01', 4, 4, '普通高等教育“十一五”国家级规划教材。'),
(13, '大学物理', '9787040502061', '2018-01-01', 4, 4, '普通高等教育“十一五”国家级规划教材。'),
(14, '1984', '9780451524935', '1949-06-08', 13, 15, 'A dystopian novel set in Airstrip One, a province of the superstate Oceania in a world of perpetual war, omnipresent government surveillance, and public manipulation.'),
(15, 'To Kill a Mockingbird', '9780062420701', '1960-07-11', 6, 6, 'A novel about the seriousness of racism and the purity of childhood innocence, set in the American South during the 1930s.'),
(16, 'The Great Gatsby', '9780743273565', '1925-04-10', 13, 6, 'A novel about the American dream, the Jazz Age, and the decline of the upper class.'),
(17, 'Pride and Prejudice', '9780679783268', '1813-01-28', 5, 6, 'A romantic novel of manners that charts the emotional development of the protagonist Elizabeth Bennet.'),
(18, 'Sapiens: A Brief History of Humankind', '9780062316097', '2015-02-10', 6, 7, 'A book that surveys the history of humankind from the Stone Age up to the twenty-first century.'),
(19, 'Educated: A Memoir', '9780399590504', '2018-02-20', 5, 16, 'A memoir detailing the author\'s journey from growing up in a strict Mormon survivalist family in rural Idaho to attending Cambridge University.'),
(20, 'Becoming', '9781524763138', '2018-11-13', 5, 9, 'The memoir of former First Lady of the United States Michelle Obama.'),
(21, 'The Diary of a Young Girl', '9780553296983', '1947-06-25', 5, 16, 'The writings from the Dutch-language diary kept by Anne Frank while she was in hiding for two years with her family during the Nazi occupation of the Netherlands.'),
(22, 'Dune', '9780441013593', '1965-08-01', 7, 5, 'A science fiction novel set in the distant future amidst a feudal interstellar society in which various noble houses control planetary fiefs.'),
(23, 'The Nightingale', '9781250080400', '2015-02-03', 9, 17, 'A historical fiction novel that tells the story of two sisters in France during World War II and their struggle to survive the German occupation.'),
(24, 'Circe', '9781408890042', '2018-04-10', 15, 8, 'A fantasy novel that retells the story of the Greek mythological figure Circe, a minor goddess and sorceress.'),
(25, 'Project Hail Mary', '9780593135204', '2021-05-04', 5, 5, 'A science fiction novel about a lone astronaut on a mission to save humanity from an extinction-level event.'),
(26, 'The Thursday Murder Club', '9781984880963', '2020-09-03', 12, 10, 'A mystery novel about a group of retirees in a peaceful retirement village who gather to solve cold cases for fun, but find themselves in the middle of a real-life murder.'),
(27, 'A People\'s History of the United States', '9780062397348', '2015-04-21', 6, 7, 'A non-fiction book that presents American history from the perspective of the common people rather than the usual historical figures.'),
(28, 'Frankenstein', '9780553212471', '1818-01-01', 5, 6, 'A classic novel of the Gothic genre, which tells the story of Victor Frankenstein, a young scientist who creates a sapient creature in an unorthodox scientific experiment.'),
(29, 'Anna Karenina', '9780143035008', '1878-01-01', 5, 6, 'A novel of literary realism that explores themes of betrayal, faith, family, marriage, Imperial Russian society, desire, and rural vs. city life.'),
(30, 'Babel', '9780063021433', '2022-08-23', 6, 8, 'An epic historical fantasy that interrogates the relationship between language, translation, and the violence of colonialism.'),
(31, 'This Present Darkness', '9780842361712', '1986-08-01', 16, 12, 'A Christian thriller novel about the spiritual warfare between angels and demons over a small town.');

-- Step 7: Link Books and Authors
INSERT INTO `Book_Authors` (`BookID`, `AuthorID`) VALUES
(1, 2),
(2, 2),
(3, 2),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1),
(9, 1),
(10, 3),
(11, 4),
(12, 5),
(13, 5),
(14, 6), 
(15, 11), 
(16, 10), 
(17, 9), 
(18, 12), 
(19, 13), 
(20, 14), 
(21, 15), 
(22, 18), 
(23, 16), 
(24, 17), 
(25, 19), 
(26, 20), 
(27, 21), 
(28, 22), 
(29, 23), 
(30, 25),
(31, 26);

-- Step 8: Insert Book Copies
-- 3 copies for each book
INSERT INTO `BookCopies` (`CopyID`, `BookID`, `Status`, `Location`) 
SELECT CONCAT(b.BookID, '-1'), b.BookID, 'Available', 'Main Shelf' FROM `Books` b UNION ALL
SELECT CONCAT(b.BookID, '-2'), b.BookID, 'Available', 'Main Shelf' FROM `Books` b UNION ALL
SELECT CONCAT(b.BookID, '-3'), b.BookID, 'Available', 'Main Shelf' FROM `Books` b;

-- Set a few copies to be 'OnLoan' or 'Reserved'
UPDATE BookCopies SET Status = 'OnLoan' WHERE CopyID IN ('15-1', '18-1', '21-1', '24-1', '27-1');
UPDATE BookCopies SET Status = 'Reserved' WHERE CopyID IN ('16-1', '19-1');
UPDATE BookCopies SET Status = 'Lost' WHERE CopyID = '23-1';

-- Step 9: Insert Borrowing Records
INSERT INTO `BorrowingRecords` (`CopyID`, `UserID`, `BorrowDate`, `DueDate`, `ReturnDate`, `Fine`) VALUES
-- Past, returned records
('14-1', 'student1', '2023-09-01', '2023-09-30', '2023-09-28', 0.00),
('17-1', 'student2', '2023-10-05', '2023-11-04', '2023-11-01', 0.00),
('20-1', 'teacher1', '2023-08-15', '2023-09-14', '2023-09-10', 0.00),
-- Current 'OnLoan' records
('15-1', 'student3', '2025-10-20', '2025-11-19', NULL, 0.00), -- Due in the future
('18-1', 'student4', '2025-10-01', '2025-10-31', NULL, 0.00), -- Overdue
('21-1', 'teacher2', '2025-09-25', '2025-10-25', NULL, 0.00), -- Overdue
('24-1', 'student1', '2025-11-01', '2025-12-01', NULL, 0.00), -- Due in the future
('27-1', 'student2', '2025-11-10', '2025-12-10', NULL, 0.00); -- Due in the future

-- Step 10: Insert Reservations
-- For a book with no available copies
INSERT INTO `Reservations` (`BookID`, `UserID`, `ReservationDate`, `Status`) VALUES
(16, 'student1', '2025-11-12', 'Pending'); 

SET FOREIGN_KEY_CHECKS=1;