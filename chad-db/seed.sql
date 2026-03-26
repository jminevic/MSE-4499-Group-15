INSERT OR IGNORE INTO test_types (test_name) VALUES
('Pronation/Supination ROM'),
('Pronation/Supination Torque'),
('Pinch Grip'),
('Radial/Ulnar Deviation ROM'),
('Wrist Flexion/Extension ROM');

INSERT OR IGNORE INTO positions (position_name) VALUES
('Quarterback'),
('Running Back'),
('Wide Receiver'),
('Tight End'),
('Offensive Lineman'),
('Defensive Lineman'),
('Linebacker'),
('Cornerback'),
('Safety'),
('Kicker'),
('Punter');

INSERT OR IGNORE INTO measurement_types (test_type_id, measurement_name, unit) VALUES
(1, 'Pronation Angle', 'deg'),
(1, 'Supination Angle', 'deg'),
(2, 'Pronation Torque', 'N·m'),
(2, 'Supination Torque', 'N·m'),
(3, 'Thumb-Index Pinch Force', 'N'),
(3, 'Thumb-Middle Pinch Force', 'N'),
(3, 'Thumb-Ring Pinch Force', 'N'),
(3, 'Thumb-Pinky Pinch Force', 'N'),
(4, 'Radial Deviation Angle', 'deg'),
(4, 'Ulnar Deviation Angle', 'deg'),
(5, 'Wrist Flexion Angle', 'deg'),
(5, 'Wrist Extension Angle', 'deg');