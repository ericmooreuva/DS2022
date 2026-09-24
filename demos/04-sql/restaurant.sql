CREATE TABLE IF NOT EXISTS states (
    state_code INT PRIMARY KEY,
    home_state VARCHAR(100)
);

INSERT INTO states (state_code, home_state) VALUES (26, 'Michigan');
INSERT INTO states (state_code, home_state) VALUES (56, 'Wyoming');

CREATE TABLE IF NOT EXISTS jobs (
    job_code VARCHAR(3) PRIMARY KEY,
    job VARCHAR(50)
);

INSERT INTO jobs (job_code, job) VALUES ('J01', 'Chef');
INSERT INTO jobs (job_code, job) VALUES ('J02', 'Waiter');
INSERT INTO jobs (job_code, job) VALUES ('J03', 'Bartender');

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT PRIMARY KEY,
    name VARCHAR(50),
    state_id INT
);

INSERT INTO employees (employee_id, name, state_id) VALUES (1, 'Alice', 26);
INSERT INTO employees (employee_id, name, state_id) VALUES (2, 'Bob', 56);
INSERT INTO employees (employee_id, name, state_id) VALUES (3, 'Alice', 56);

CREATE TABLE IF NOT EXISTS employees_jobs (
    employee_id INT,
    job_code VARCHAR(3),
    PRIMARY KEY (employee_id, job_code)
);

INSERT INTO employees_jobs (employee_id, job_code) VALUES (1, 'J01');
INSERT INTO employees_jobs (employee_id, job_code) VALUES (1, 'J02');
INSERT INTO employees_jobs (employee_id, job_code) VALUES (2, 'J02');
INSERT INTO employees_jobs (employee_id, job_code) VALUES (2, 'J03');
INSERT INTO employees_jobs (employee_id, job_code) VALUES (3, 'J01');
