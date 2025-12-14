-- PostgreSQL script to create tables for Library Management System
-- Based on the schema defined in README.md

-- Create database (run this separately if needed)
-- CREATE DATABASE library_management;

-- Use the database
-- \c library_management;

-- Create book table
CREATE TABLE book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(17) UNIQUE,
    publisher VARCHAR(255),
    publication_year INTEGER,
    genre VARCHAR(100)
);

-- Create book_copy table
CREATE TABLE book_copy (
    book_copy_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('available', 'loaned', 'damaged', 'lost'))
);

-- Create member table
CREATE TABLE member (
    member_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(254) UNIQUE NOT NULL,
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'suspended'))
);

-- Create employee table
CREATE TABLE employee (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL
);

-- Create loan table
CREATE TABLE loan (
    loan_id SERIAL PRIMARY KEY,
    book_copy_id INTEGER NOT NULL REFERENCES book_copy(book_copy_id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES member(member_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employee(employee_id) ON DELETE SET NULL,
    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    actual_return_date DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('in_progress', 'returned', 'overdue'))
);

-- Optional: Create indexes for performance
CREATE INDEX idx_book_copy_book_id ON book_copy(book_id);
CREATE INDEX idx_loan_book_copy_id ON loan(book_copy_id);
CREATE INDEX idx_loan_member_id ON loan(member_id);
CREATE INDEX idx_loan_employee_id ON loan(employee_id);