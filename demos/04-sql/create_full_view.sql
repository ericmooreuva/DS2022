CREATE OR REPLACE VIEW full_view AS SELECT
    e.employee_id,
    e.name,
    s.home_state,
    j.job
FROM employees_jobs AS ej
LEFT JOIN employees e ON ej.employee_id = e.employee_id
LEFT JOIN states s ON e.state_id = s.state_code
LEFT JOIN jobs j ON ej.job_code = j.job_code;
