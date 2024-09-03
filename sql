SELECT 
    TO_CHAR(TO_DATE(alert_time, 'HH24:MI:SS'), 'HH24') AS alert_hour,
    COUNT(*) AS alert_count
FROM 
    your_table_name
GROUP BY 
    TO_CHAR(TO_DATE(alert_time, 'HH24:MI:SS'), 'HH24')
ORDER BY 
    alert_hour;
