
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- Rename the test type so the UI reflects the new terminology.
UPDATE test_types
SET test_name = 'Pinch Test'
WHERE test_name = 'Pinch Grip';

-- Remove old pinch-test result data because the measurement structure changed
-- from 4 finger-specific types to 3 pinch-type categories.
DELETE FROM trial_values
WHERE result_set_id IN (
    SELECT rs.result_set_id
    FROM result_sets rs
    JOIN measurement_types mt ON rs.measurement_type_id = mt.measurement_type_id
    WHERE mt.test_type_id = (
        SELECT test_type_id FROM test_types WHERE test_name = 'Pinch Test'
    )
);

DELETE FROM result_sets
WHERE measurement_type_id IN (
    SELECT measurement_type_id
    FROM measurement_types
    WHERE test_type_id = (
        SELECT test_type_id FROM test_types WHERE test_name = 'Pinch Test'
    )
);

DELETE FROM test_instances
WHERE test_type_id = (
    SELECT test_type_id FROM test_types WHERE test_name = 'Pinch Test'
);

-- Replace the old pinch measurement definitions.
DELETE FROM measurement_types
WHERE test_type_id = (
    SELECT test_type_id FROM test_types WHERE test_name = 'Pinch Test'
);

INSERT INTO measurement_types (test_type_id, measurement_name, unit)
SELECT test_type_id, 'Lateral Pinch Force', 'N'
FROM test_types
WHERE test_name = 'Pinch Test';

INSERT INTO measurement_types (test_type_id, measurement_name, unit)
SELECT test_type_id, 'Three-Point Pinch Force', 'N'
FROM test_types
WHERE test_name = 'Pinch Test';

INSERT INTO measurement_types (test_type_id, measurement_name, unit)
SELECT test_type_id, 'Two-Point Pinch Force', 'N'
FROM test_types
WHERE test_name = 'Pinch Test';

COMMIT;
