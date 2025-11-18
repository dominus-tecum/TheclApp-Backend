
-- TEST DATA VALIDATION QUERIES
-- Use these to validate your test scenarios

-- 1. Validate gynecologic data patterns
SELECT 
    patient_id,
    patient_name,
    COUNT(*) as entry_count,
    MIN(submission_date) as first_entry,
    MAX(submission_date) as last_entry
FROM gynecologic_surgery_entries 
GROUP BY patient_id, patient_name
ORDER BY entry_count DESC;

-- 2. Validate urologic data patterns  
SELECT 
    patient_id,
    patient_name, 
    COUNT(*) as entry_count,
    MIN(submission_date) as first_entry,
    MAX(submission_date) as last_entry
FROM urological_surgery_entries
GROUP BY patient_id, patient_name
ORDER BY entry_count DESC;

-- 3. Cross-specialty validation
SELECT 
    g.patient_id,
    g.patient_name,
    COUNT(DISTINCT g.submission_date) as gyn_dates,
    COUNT(DISTINCT u.submission_date) as uro_dates,
    COUNT(DISTINCT CASE WHEN g.submission_date = u.submission_date THEN g.submission_date END) as same_day_entries
FROM gynecologic_surgery_entries g
LEFT JOIN urological_surgery_entries u ON g.patient_id = u.patient_id
GROUP BY g.patient_id, g.patient_name
HAVING uro_dates > 0;

-- 4. Data completeness check
SELECT 
    'gynecologic' as table_name,
    COUNT(*) as total,
    SUM(CASE WHEN condition_data IS NULL OR condition_data = '{}' THEN 1 ELSE 0 END) as empty_data
FROM gynecologic_surgery_entries
UNION ALL
SELECT 
    'urological' as table_name, 
    COUNT(*) as total,
    SUM(CASE WHEN condition_data IS NULL OR condition_data = '{}' THEN 1 ELSE 0 END) as empty_data
FROM urological_surgery_entries;
