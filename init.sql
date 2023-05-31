CREATE DATABASE ticketing_system;
CREATE USER ticketing_user WITH PASSWORD 'qwerty123';
GRANT ALL PRIVILEGES ON DATABASE ticketing_system TO ticketing_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ticketing_user;