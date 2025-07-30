DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Messages CASCADE;

CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    profile_picture TEXT
);

CREATE TABLE Messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES Users(user_id),
    receiver_id INTEGER REFERENCES Users(user_id),
    message_text TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
