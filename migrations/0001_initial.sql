-- AI Content Generator Schema v1

-- Drop tables if they exist to make this script rerunnable
DROP TABLE IF EXISTS social_connections;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS content_history;
DROP TABLE IF EXISTS credits;
DROP TABLE IF EXISTS users;

-- User table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone_number TEXT UNIQUE,
    email_otp TEXT,
    sms_otp TEXT,
    is_verified INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Credits table
CREATE TABLE credits (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 10,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Content History table
CREATE TABLE content_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    input_params TEXT NOT NULL, -- JSON blob
    generated_text TEXT NOT NULL,
    generated_image_url TEXT,
    status TEXT NOT NULL DEFAULT 'draft', -- e.g., 'draft', 'posted_x'
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    gateway TEXT NOT NULL,
    gateway_txn_id TEXT NOT NULL UNIQUE,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    credits_purchased INTEGER NOT NULL,
    status TEXT NOT NULL, -- e.g., 'pending', 'completed', 'failed'
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Social Connections table
CREATE TABLE social_connections (
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL, -- 'x_com', 'linkedin'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TEXT,
    profile_id TEXT NOT NULL,
    PRIMARY KEY (user_id, platform),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
