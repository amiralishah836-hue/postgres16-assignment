-- SDL Database Schema
-- Task 3

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE threats (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    threat_type VARCHAR(50),
    severity VARCHAR(20),
    status VARCHAR(20)
);

CREATE TABLE vulnerabilities (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    cvss_score NUMERIC(3,1),
    status VARCHAR(20),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mitigations (
    id SERIAL PRIMARY KEY,
    threat_id INTEGER NOT NULL REFERENCES threats(id) ON DELETE CASCADE,
    control TEXT NOT NULL,
    implemented BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase VARCHAR(50),
    reviewer VARCHAR(100),
    result VARCHAR(50),
    review_date DATE
);
