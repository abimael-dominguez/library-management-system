-- PostgreSQL schema for the Library Management System
-- Source of truth for the live application schema is src/infrastructure/models.py
-- This SQL file is a PostgreSQL-oriented equivalent of the current SQLAlchemy model layer.

-- Create database separately if needed:
-- CREATE DATABASE library_management;
-- \c library_management;

-- ---------------------------------------------------------------------------
-- book
-- Stores metadata for a title, not individual physical copies.
-- ---------------------------------------------------------------------------
CREATE TABLE book (
    book_id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(17) UNIQUE,
    publisher VARCHAR(255),
    publication_year INTEGER,
    genre VARCHAR(100),
    pages INTEGER,
    max_loan_weeks INTEGER NOT NULL DEFAULT 3,
    total_copies INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_book_title ON book(title);
CREATE INDEX idx_book_author ON book(author);

-- ---------------------------------------------------------------------------
-- book_copy
-- Stores each physical copy of a book.
-- ---------------------------------------------------------------------------
CREATE TABLE book_copy (
    book_copy_id VARCHAR(64) PRIMARY KEY,
    book_id VARCHAR(36) NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_book_copy_status CHECK (status IN ('available', 'loaned', 'damaged', 'lost'))
);

CREATE INDEX idx_book_copy_book_id ON book_copy(book_id);

-- ---------------------------------------------------------------------------
-- member
-- Stores library patron information.
-- ---------------------------------------------------------------------------
CREATE TABLE member (
    member_id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(254) NOT NULL UNIQUE,
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_member_status CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_member_first_name ON member(first_name);
CREATE INDEX idx_member_last_name ON member(last_name);

-- ---------------------------------------------------------------------------
-- employee
-- Stores staff members involved in loan processing.
-- ---------------------------------------------------------------------------
CREATE TABLE employee (
    employee_id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- loan
-- Stores a borrowing transaction for a specific physical copy.
-- ---------------------------------------------------------------------------
CREATE TABLE loan (
    loan_id VARCHAR(36) PRIMARY KEY,
    book_copy_id VARCHAR(64) NOT NULL REFERENCES book_copy(book_copy_id) ON DELETE CASCADE,
    member_id VARCHAR(36) NOT NULL REFERENCES member(member_id) ON DELETE CASCADE,
    employee_id VARCHAR(36) REFERENCES employee(employee_id) ON DELETE SET NULL,
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    actual_return_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_loan_status CHECK (status IN ('in_progress', 'returned', 'overdue')),
    CONSTRAINT ck_due_date_after_loan_date CHECK (due_date >= loan_date),
    CONSTRAINT ck_actual_return_after_loan_date CHECK (
        actual_return_date IS NULL OR actual_return_date >= loan_date
    )
);

CREATE INDEX idx_loan_book_copy_id ON loan(book_copy_id);
CREATE INDEX idx_loan_member_id ON loan(member_id);
CREATE INDEX idx_loan_employee_id ON loan(employee_id);

-- Only one active loan per copy is allowed.
CREATE UNIQUE INDEX idx_loan_one_active_copy
    ON loan(book_copy_id)
    WHERE status = 'in_progress';
