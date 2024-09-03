WITH MayJobCounts AS (
    SELECT 
        APP_GROUP,
        APP_ID,
        COB_DATE,
        JOB_COUNT,
        ROW_NUMBER() OVER (PARTITION BY APP_GROUP, APP_ID ORDER BY COB_DATE ASC) AS rn_asc,
        ROW_NUMBER() OVER (PARTITION BY APP_GROUP, APP_ID ORDER BY COB_DATE DESC) AS rn_desc
    FROM 
        your_table_name
    WHERE 
        COB_DATE BETWEEN TO_DATE('2023-05-01', 'YYYY-MM-DD') AND TO_DATE('2023-05-31', 'YYYY-MM-DD')
)
SELECT 
    m1.APP_GROUP,
    m1.APP_ID,
    m1.JOB_COUNT AS JOB_COUNT_START,
    m2.JOB_COUNT AS JOB_COUNT_END,
    (m2.JOB_COUNT - m1.JOB_COUNT) AS JOB_COUNT_CHANGE
FROM 
    MayJobCounts m1
JOIN 
    MayJobCounts m2 
    ON m1.APP_GROUP = m2.APP_GROUP 
    AND m1.APP_ID = m2.APP_ID
WHERE 
    m1.rn_asc = 1 
    AND m2.rn_desc = 1;



SELECT 
    batch_region,
    batch_severity,
    COUNT(*) AS severity_count
FROM 
    your_table_name
GROUP BY 
    batch_region, 
    batch_severity
ORDER BY 
    batch_region,
    CASE 
        WHEN batch_severity = 'high' THEN 1
        WHEN batch_severity = 'medium' THEN 2
        WHEN batch_severity = 'low' THEN 3
    END;
