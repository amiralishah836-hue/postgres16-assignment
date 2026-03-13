-- SDL Demo Data
-- Task 3

-- Insert Projects
INSERT INTO projects (name, description, owner)
VALUES
('SecureBank API', 'Online banking backend system', 'Alice'),
('HealthTrack App', 'Healthcare monitoring platform', 'Bob');

-- Insert Threats
INSERT INTO threats (project_id, title, threat_type, severity, status)
VALUES
(1, 'SQL Injection', 'Injection', 'High', 'Open'),
(1, 'Broken Authentication', 'Authentication', 'Critical', 'Open'),
(2, 'Sensitive Data Exposure', 'Data Leakage', 'High', 'Mitigated');

-- Insert Vulnerabilities
INSERT INTO vulnerabilities (project_id, name, cvss_score, status)
VALUES
(1, 'Unsanitized Input in Login', 8.5, 'Open'),
(1, 'Weak Password Policy', 6.5, 'In Progress'),
(2, 'Unencrypted API Traffic', 7.2, 'Closed');

-- Insert Mitigations
INSERT INTO mitigations (threat_id, control, implemented, verified)
VALUES
(1, 'Use parameterized queries', TRUE, TRUE),
(2, 'Implement MFA', TRUE, FALSE),
(3, 'Enable TLS 1.3', TRUE, TRUE);

-- Insert Assessments
INSERT INTO assessments (project_id, phase, reviewer, result, review_date)
VALUES
(1, 'Design Review', 'Charlie', 'Approved', '2025-01-10'),
(1, 'Penetration Testing', 'David', 'Issues Found', '2025-02-01'),
(2, 'Code Review', 'Eve', 'Approved', '2025-01-15');
