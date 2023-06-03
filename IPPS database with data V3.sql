DROP SCHEMA IF EXISTS ipps;
CREATE SCHEMA ipps;
USE ipps;


CREATE TABLE user (
    user_name VARCHAR(50) PRIMARY KEY,
    password VARCHAR(200) NOT NULL,
    role CHAR(20) NOT NULL,
    link VARCHAR(300)
);

CREATE TABLE notification (
    notification_id INT PRIMARY KEY auto_increment,
    subjects VARCHAR(200) NOT NULL,
    Send_from VARCHAR(100) NOT NULL,
    send_to VARCHAR(100) NOT NULL,
    message VARCHAR(500) NOT NULL,
    receive_date VARCHAR(100) NOT NULL,
    status ENUM('read', 'unread') NOT NULL
);
    
CREATE TABLE staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_name) REFERENCES user(user_name) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE mentor (
    mentor_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    company_name VARCHAR(50) NOT NULL,
	email VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    location VARCHAR(150) NOT NULL,
    FOREIGN KEY (user_name) REFERENCES user(user_name) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE project (
    project_id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_id INT NOT NULL,
    project_title VARCHAR(100) NOT NULL,
    project_summary VARCHAR(500) NOT NULL,
    place_num INT NOT NULL,
    start_date DATE NOT NULL,
    FOREIGN KEY (mentor_id) REFERENCES mentor(mentor_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE skills (
    skill_id INT PRIMARY KEY ,
    details VARCHAR(50) NOT NULL
);


CREATE TABLE project_requirement (
    project_req_id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    skill_id INT NOT NULL,
	FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    preferred_name VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    location ENUM('Auckland', 'Christchurch', 'Hamilton', 'Wellington', 'Other') NOT NULL,
    cv_link VARCHAR(250),
    currently_enrolled BOOLEAN NOT NULL DEFAULT 1,
    semester_to_place INT NOT NULL DEFAULT 2,
    need_project BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_name) REFERENCES user(user_name) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE student_skills(
	student_skill_no INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    skill_id INT NOT NULL, 
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE wishlist(
	wishlist_no INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    project_id INT NOT NULL,
    ranking INT NOT NULL,
	submission_status ENUM('Submitted', 'Drafted') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE placement(
	placement_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    project_id INT NOT NULL,
    pl_status ENUM('Matched', 'Interviewed', 'Not Interested', 'Confirmed', 'Cancelled','Intervention Needed') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE ON UPDATE CASCADE
);



INSERT INTO user (user_name, password, role)
VALUES 
-- student data
    ('rgreen', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('jlee', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('abrown', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('mtaylor', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('aliu', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('fwong', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('lchen', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('lkim', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('canderson', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('gscott', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('rdavis', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('pdavis', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('jchen', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('lkim2', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('mlee', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('abrown2', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('smartin', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('hliu', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('rsong', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('mjohnson', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('sbrown', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('ckim', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('jli', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('sliu', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('mbrown', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('ajohnson', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('jjones', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('smartin2', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('mharris', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('rmartin', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('mjones', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('mdavis', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('hbrown', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('klee', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),    
    ('cwilliams', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),  
	('jlee2', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),  
	('gdavis', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),  
	('sjohnson', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),  
	('ajohnson2', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),  
	('mturner', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
	('jharrison', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    ('dmiller', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'student'),
    -- staff data 
    ('msteven', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
	('ncowden', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
    ('lyang', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
	('ayohanes', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
    ('adupont', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
	('myoung', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
    ('tng', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
	('cstrange', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
    ('kkiri', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'staff'),
    -- mentor data 
	('tommyd', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('fredc', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('rachels', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
    ('jasonl', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('antonym', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('dougaly', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('marka', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('alang', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('fionan', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('lisas', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
    ('stephenb', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('geoffc', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('heidiw', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('leahb', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('campbellg', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('granta', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('rodneys', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('robp', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('meganx', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('mariea', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('heatherm', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('kelving', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('timg', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor'),
	('paulas', '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c', 'mentor');


INSERT INTO skills (skill_id, details) VALUES 
('1', 'Python'),('2', 'Javascript'),('3', 'HTML/CSS'),('4', 'Database/SQL'),('5', 'User Experience'),('6', 'UI Design'),('7', 'Content Creation'),
('8', 'Business analysis'),('9', 'GIS'),('10', 'Neural neworks'),('11', 'Node.js'),('12', 'React.js'),('13', 'Angular.js');


INSERT INTO student (student_id, user_name, first_name, last_name, preferred_name, email, phone, location, cv_link, currently_enrolled, semester_to_place, need_project) VALUES
(1001, 'rgreen', 'Rachel', 'Green', 'Rachel', 'rgreen@lincolnuni.ac.nz', '0211234567', 'Auckland', NULL, 1, 2, 1),
(1002, 'jlee', 'Jason', ' Lee', 'Jason', 'jlee@lincolnuni.ac.nz', '0212345678', 'Auckland', NULL, 1, 2, 1),
(1003, 'abrown', 'Antony', ' Brown', 'Tony', 'abrown@lincolnuni.ac.nz', '0213456789', 'Christchurch', NULL, 1, 2, 1),
(1004, 'mtaylor', 'Mark', ' Taylor', 'Mark', 'mtaylor@lincolnuni.ac.nz', '0214567890', 'Christchurch', NULL, 1, 2, 1),
(1005, 'aliu', 'Alan', ' Liu', 'Alan', 'aliu@lincolnuni.ac.nz', '0215678901', 'Hamilton', NULL, 1, 2, 1),
(1006, 'fwong', 'Fiona', ' Wong', 'Fiona', 'fwong@lincolnuni.ac.nz', '0216789012', 'Hamilton', NULL, 1, 2, 1),
(1007, 'lchen', 'Lisa', ' Chen', 'Lisa', 'lchen@lincolnuni.ac.nz', '0217890123', 'Auckland', NULL, 1, 2, 1),
(1008, 'lkim', 'Leah', ' Kim', 'Leah', 'lkim@lincolnuni.ac.nz', '0218901234', 'Hamilton', NULL, 1, 2, 1),
(1009, 'canderson', 'Campbell', ' Anderson', 'Campbell', 'canderson@lincolnuni.ac.nz', '0219012345', 'Auckland', NULL, 1, 2, 1),
(1010, 'gscott', 'Grant', ' Scott', 'Grant', 'gscott@lincolnuni.ac.nz', '0210123456', 'Auckland', NULL, 1, 2, 1),
(1011, 'rdavis', 'Rodney', ' Davis', 'Rodney', 'rdavis@lincolnuni.ac.nz', '0211234567', 'Hamilton', NULL, 1, 2, 1),
(1012, 'pdavis', 'Phil', ' Davis', 'Phil', 'pdavis@lincolnuni.ac.nz', '0212345678', 'Auckland', NULL, 1, 2, 1),
(1013, 'jchen', 'Julia', ' Chen', 'Julia', 'jchen@lincolnuni.ac.nz', '0213456789', 'Auckland', NULL, 1, 2, 1),
(1014, 'lkim2', 'Lee', ' Kim', 'Lee', 'lkim2@lincolnuni.ac.nz', '0214567890', 'Auckland', Null, 1, 2, 0),
(1015, 'mlee', 'Michelle', ' Lee', 'Michelle', 'mlee@lincolnuni.ac.nz', '0215678901', 'Auckland', NULL, 1, 2, 1),
(1016, 'abrown2', 'Andrew', ' Brown', 'Andrew', 'abrown@lincolnuni.ac.nz', '0216789012', 'Christchurch', NULL, 1, 2, 1),
(1017, 'smartin', 'Steve', ' Martin', 'Steve', 'smartin@lincolnuni.ac.nz', '0217890123', 'Auckland', NULL, 1, 2, 1),
(1018, 'hliu', 'Hannah', ' Liu', 'Hannah', 'hliu@lincolnuni.ac.nz', '0218901234', 'Wellington', NULL, 1, 2, 1),
(1019, 'rsong', 'Robert', ' Song', 'Robert', 'rsong@lincolnuni.ac.nz', '0219012345', 'Christchurch', NULL, 1, 2, 1),
(1020, 'mjohnson', 'Mark', ' Johnson', 'Mark', 'mjohnson@lincolnuni.ac.nz', '0210123456', 'Auckland', NULL, 1, 2, 1),
(1021, 'sbrown', 'Sophie', ' Brown', 'Sophie', 'sbrown@lincolnuni.ac.nz', '0211234567', 'Christchurch', NULL, 1, 2, 1),
(1022, 'ckim', 'Chris', ' Kim', 'Chris', 'ckim@lincolnuni.ac.nz', '0212345678', 'Wellington', NULL, 1, 2, 1),
(1023, 'jli', 'Jessica', ' Li', 'Jessica', 'jli@lincolnuni.ac.nz', '0213456789', 'Christchurch', NULL, 1, 2, 1),
(1024, 'sliu', 'Samantha', ' Liu', 'Samantha', 'sliu@lincolnuni.ac.nz', '0214567890', 'Christchurch', NULL, 1, 2, 1),
(1025, 'mbrown', 'Mary', ' Brown', 'Mary', 'mbrown@lincolnuni.ac.nz', '0215678901', 'Auckland', NULL, 1, 2, 0),
(1026, 'ajohnson', 'Alex', ' Johnson', 'Alex', 'ajohnson@lincolnuni.ac.nz', '0216789012', 'Wellington', NULL, 1, 2, 1),
(1027, 'jjones', 'Julie', ' Jones', 'Julie', 'jjones@lincolnuni.ac.nz', '0217890123', 'Christchurch', NULL, 1, 2, 1),
(1028,'smartin2', 'Steve', ' Martin', 'Steve', 'smartin@lincolnuni.ac.nz', '0217890123', 'Auckland', NULL, 1, 2, 1),
(1029, 'mharris', 'Mark', ' Harris', 'Mark', 'mharris@lincolnuni.ac.nz', '0218901234', 'Hamilton', NULL, 1, 2, 1),
(1030, 'rmartin', 'Rob', ' Martin', 'Rob', 'rmartin@lincolnuni.ac.nz', '0219012345', 'Other', NULL, 1, 2, 1),
(1031, 'mjones', 'Megan', ' Jones', 'Megan', 'mjones@lincolnuni.ac.nz', '0210123456', 'Auckland', NULL, 1, 2, 1),
(1032, 'mdavis', 'Marie', ' Davis', 'Marie', 'mdavis@lincolnuni.ac.nz', '0212345678', 'Other', NULL, 1, 2, 1),
(1033, 'hbrown', 'Heather', ' Brown', 'Heather', 'hbrown@lincolnuni.ac.nz', '0213456789', 'Auckland', NULL, 1, 2, 1),
(1034, 'klee', 'Kelvin', ' Lee', 'Kelvin', 'klee@lincolnuni.ac.nz', '0214567890', 'Hamilton', NULL, 1, 2, 1),
(1035, 'cwilliams', 'Charlotte', ' Williams', 'Charlotte', 'cwilliams@lincolnuni.ac.nz', '0215678901', 'Christchurch', NULL, 1, 2, 1),
(1036, 'jlee2', 'Justine', ' Lee', 'Justine', 'jlee2@lincolnuni.ac.nz', '0216789012', 'Hamilton', NULL, 1, 2, 1),
(1037, 'gdavis', 'Gill', ' Davis', 'Gill', 'gdavis@lincolnuni.ac.nz', '0217890123', 'Other', NULL, 1, 2, 1),
(1038, 'sjohnson', 'Sean', ' Johnson', 'Sean', 'sjohnson@lincolnuni.ac.nz', '0218901234', 'Christchurch', NULL, 1, 2, 1),
(1039, 'ajohnson2', 'Amy', ' Johnson', 'Amy', 'ajohnson@lincolnuni.ac.nz', '0219012345', 'Other', NULL, 1, 2, 0),
(1040, 'mturner', 'Mark', ' Turner', 'Mark', 'mturner@lincolnuni.ac.nz', '0210123456', 'Auckland', NULL, 1, 2, 0),
(1041, 'jharrison', 'James', ' Harrison', 'James', 'jharrison@lincolnuni.ac.nz', '0212345678', 'Other', NULL, 1, 2, 0),
(1042, 'dmiller', 'David', ' Miller', 'David', 'dmiller@lincolnuni.ac.nz', '0213456789', 'Hamilton', NULL, 1, 2, 0);


INSERT INTO staff (staff_id, user_name, first_name, last_name, email, phone)
VALUES
(323, 'msteven', 'Manaia', 'Steven', 'msteven@lincolnuni.ac.nz', '0270750712'),
(331, 'ncowden', 'Nikora', 'Cowden', 'ncowden@lincolnuni.ac.nz', '0222983223'),
(339, 'lyang', 'Lian', 'Yang', 'lyang@lincolnuni.ac.nz', '0275442649'),
(340, 'ayohanes', 'Yohanes', 'Chen', 'ayohanes@lincolnuni.ac.nz', '0224589419'),
(353, 'adupont', 'Antoine', 'Dupont', 'adupont@lincolnuni.ac.nz', '0210244493'),
(358, 'myoung', 'Marshall', 'Young', 'myoung@lincolnuni.ac.nz', '0214722954'),
(376, 'tng', 'Trinh', 'Ng', 'tng@lincolnuni.ac.nz', 02242158),
(386, 'cstrange', 'Connell', 'Strange', 'cstrange@lincolnuni.ac.nz', 026432458),
(390, 'kkiri', 'Kiri', 'Xun', 'kkiri@lincolnuni.ac.nz', 02962298);


INSERT INTO mentor (mentor_id, user_name, first_name, last_name, company_name, email, phone, industry, location)
VALUES
(501, 'tommyd', 'Tommy', 'Davidson', 'Cybrospace', 'tommy.davidson@cybrospace.co.nz', '021579845', 'Cybersecurity', 'Auckland'),
(502, 'fredc', 'Fred', 'Chia', 'WebHive', 'fred.chia@webhive.co.nz', '027964802', 'Website Development', 'Hamilton'),
(503, 'rachels', 'Rachel', 'Savea', 'TechWise', 'rachel.savea@techwise.co.nz', '027045678', 'IT Consulting', 'Christchurch'),
(504, 'jasonl', 'Jason', 'Liang', 'CodeCraft', 'jason.liang@codecraft.co.nz', '021873100', 'Software Development', 'Online'),
(505, 'antonym', 'Antony', 'May', 'WebWizards', 'antony.may@webwizards.co.nz', '027983042', 'Web Development', 'Auckland'),
(506, 'dougaly', 'Dougal', 'Yeung', 'DataDriven', 'dougal.yeung@datadriven.co.nz', '021577000', 'Data Analytics', 'Hamilton'),
(507, 'marka', 'Mark', 'Anderson', 'AppForge', 'mark.anderson@appforge.co.nz', '027099999', 'Mobile App Development', 'Christchurch'),
(508, 'alang', 'Alan', 'Gully', 'AI Innovations', 'alan.gully@aiinnovations.co.nz', '027342983', 'Artificial Intelligence', 'Online'),
(509, 'fionan', 'Fiona', 'Ngata', 'Cloudify', 'fiona.ngata@cloudify.co.nz', '021873621', 'Cloud Computing', 'Auckland'),
(510, 'lisas', 'Lisa', 'Smith', 'NetWise', 'lisa.smith@netwise.co.nz', '027980008', 'Network Security', 'Hamilton'),
(511, 'stephenb', 'Stephen', 'Brown', 'SoftSolutions', 'stephen.brown@softsolutions.co.nz', '027075622', 'Software Development', 'Christchurch'),
(512, 'geoffc', 'Geoff', 'Chen', 'CodeCrushers', 'geoff.chen@codecrushers.co.nz', '021573222', 'Software Development', 'Online'),
(513, 'heidiw', 'Heidi', 'Wang', 'TechBridge', 'heidi.wang@techbridge.co.nz', '027967777', 'IT Consulting', 'Auckland'),
(514, 'leahb', 'Leah', 'Bedecs', 'TechAlign', 'leah.bedecs@techalign.co.nz', '027044444', 'IT Infrastructure', 'Hamilton'),
(515, 'campbellg', 'Campbell', 'Gratacos', 'TechSavvy', 'campbell.gratacos@techsavvy.co.nz', '021870000', 'IT Training and Support', 'Christchurch'),
(516, 'granta', 'Grant', 'Axen', 'DataCrushers', 'grant.axen@datacrushers.co.nz', '027985555',  'Data Analytics', 'Online'),
(517, 'rodneys', 'Rodney', 'Smith',  'CodeHive','rodney.smith@codehive.co.nz', '021571111', 'Software Development', 'Auckland'),
(518, 'robp', 'Rob', 'Pérez-Olaeta',  'CloudCastles','rob.perezo@cloudcastles.co.nz', '027999999', 'Cloud Computing', 'Hamilton'),
(519, 'meganx', 'Megan', 'Xie',  'AppFusion', 'megan.xie@appfusion.co.nz','027988888', 'Mobile App Development', 'Christchurch'),
(520, 'mariea', 'Marie', 'Andersen', 'SystemSolutions', 'marie.andersen@systemsolutions.co.nz', '027977777', 'IT Consulting', 'Online'),
(521, 'heatherm', 'Heather', 'Mortensen',  'WebGo', 'heather.mortensen@webgo.co.nz','027966666', 'Website Development', 'Auckland'),
(522, 'kelving', 'Kelvin', 'Gupta',  'SmartSoft','kelvin.gupta@smartsoft.co.nz', '027955555', 'Software Development', 'Online'),
(523, 'timg', 'Tim', 'Gupta','ToWeb', 'tim.gupta@toweb.co.nz',  '027985555', 'Website Development', 'Online'),
(524, 'paulas', 'Paula', 'Sharma','WebFusion',  'paula.sharma@webfusion.co.nz', '021571111', 'Web Design', 'Auckland');


INSERT INTO project (project_id, mentor_id, project_title, project_summary, place_num, start_date) 
VALUES 
(9001, 501, 'Cybersecurity Enhancement', "Conduct a comprehensive analysis of Cybrospace's current cybersecurity measures and propose improvements to enhance the company's protection against cyber attacks.", 1, '2023-07-01'),
(9002, 502, 'Web Development for E-commerce Site', 'Develop a new e-commerce website for WebHive using the latest web development tools and techniques.', 2, '2023-07-01'),
(9003, 503, 'IT Infrastructure Upgrade', "Analyze TechWise's current IT infrastructure and propose upgrades to improve its efficiency and reliability.", 3, '2023-07-01'),
(9004, 504, 'Software Development for Project Management Tool', 'Develop a new software tool for CodeCraft that will streamline project management processes and increase efficiency.', 4, '2023-07-01'),
(9005, 505, 'Website Redesign', "Redesign WebWizards' current website to improve user experience, attract more visitors, and increase engagement.", 1, '2023-07-01'),
(9006, 506, "Data Analytics for Sales Performance", "Analyze DataDriven's sales data and provide insights and recommendations to improve sales performance.", 2, '2023-07-01'),
(9007, 507, 'Mobile App Development for Customer Engagement', 'Develop a new mobile app for AppForge that will enhance customer engagement and increase brand loyalty.', 3, '2023-07-01'),
(9008, 508, "Artificial Intelligence Implementation", 'Implement artificial intelligence (AI) technology in AI Innovations operations to improve efficiency and automate processes.', 4, '2023-07-01'),
(9009, 509, 'Cloud Management System Upgrade', 'The project aims to upgrade the cloud management system used by Cloudify, a cloud computing company, to ensure it is efficient, reliable and secure. The upgrade will include the latest security features, better automation of cloud services and an improved user interface.', 4, '2023-07-01'),
(9010, 510, 'Network Security Audit and Recommendations', 'NetWise, a network security company, is seeking an audit of their current security measures to identify potential vulnerabilities and recommend ways to improve their security posture. The project will include an assessment of their network infrastructure, firewalls, intrusion detection systems, and other security measures.', 2, '2023-07-15'),
(9011, 511, 'Custom Software Development for Client', 'SoftSolutions, a software development company, has been contracted to develop a custom software solution for a client. The project will include requirements gathering, design, development, testing and deployment of the software to meet the clients needs.', 3, '2023-07-01'),
(9012, 512, 'Code Review and Optimization', "CodeCrushers, a software development company, will conduct a code review and optimization project for a client. The project will include a thorough review of the client's existing code base, identifying potential performance bottlenecks and optimization opportunities to improve the overall quality of the software.", 2, '2023-07-01'),
(9013, 513, 'IT Strategy and Planning', "TechBridge, an IT consulting company, will lead a project to develop an IT strategy and planning roadmap for a client. The project will include an analysis of the client's current IT infrastructure and processes, identifying areas for improvement and recommending a plan for future growth.", 1, '2023-07-01'),
(9014, 514, 'IT Infrastructure Upgrade', "TechAlign, an IT infrastructure company, will upgrade the clients IT infrastructure to ensure it is reliable, secure and scalable. The project will include a review of the current infrastructure, recommending upgrades and implementing new hardware and software as necessary.", 2, '2023-07-01'),
(9015, 515, 'IT Training and Support', 'TechSavvy, an IT training and support company, will provide customized training and support to a clients employees to improve their technology skills and ensure they are using the companys IT systems effectively. The project will include developing training materials, conducting training sessions and providing ongoing support.', 3, '2023-07-01'),
(9016, 516, 'Big Data Analytics', "DataCrushers, a data analytics company, will lead a project to analyze a client's big data to identify key insights and trends. The project will include data integration, analysis, visualization and reporting to help the client make data-driven business decisions.", 2, '2023-07-01'),
(9017, 517, 'Software Development for Mobile App', "CodeHive, a software development company, will develop a mobile app for a client. The project will include requirements gathering, design, development, testing and deployment of the mobile app to meet the client's needs.", 2, '2023-07-01'),
(9018,518, 'Cloud Migration', "CloudCastles, a cloud computing company, will lead a project to migrate a client's on-premise infrastructure to the cloud. The project will include a review of the current infrastructure, identifying cloud services, data migration and testing to ensure a seamless transition to the cloud.", 2, '2023-07-01'),
(9019,519, 'Mobile App Development for E-commerce', "AppFusion, a mobile app development company, will develop a mobile app for a client's e-commerce business. The project will include requirements gathering, design, development, testing and deployment of the mobile app to meet the client's needs.", 2, '2023-07-01'),
(9020,520, 'IT Infrastructure Upgrade', 'SystemSolutions is seeking a placement student to help upgrade their current IT infrastructure to improve efficiency and security. The student will work with the IT team to assess the current infrastructure, identify areas for improvement, and implement upgrades such as cloud migration, network security enhancements, and software updates.', 1, '2023-07-01'),
(9021, 521, 'E-Commerce Website Development', "WebGo is looking for a placement student to help develop an e-commerce website for a new product line. The student will work with the web development team to design and develop the website, integrate payment and shipping systems, and ensure a smooth user experience.", 1, '2023-07-01'),
(9022, 522, 'Mobile App Development', "SmartSoft is seeking a placement student to help develop a mobile app for their software product. The student will work with the software development team to design and develop the app, implement user feedback, and ensure compatibility with multiple mobile platforms.", 1, '2023-07-01'),
(9023, 523, 'Website SEO Optimization', "ToWeb is looking for a placement student to help optimize their website for search engine rankings. The student will work with the web design team to identify opportunities for improvement, implement on-page and off-page optimization techniques, and monitor and report on results.", 1, '2023-07-01'),
(9024, 524, 'Website Redesign and Content Creation', " WebFusion is seeking a placement student to help redesign their website and create new content. The student will work with the web design and content creation teams to update the website design, create new pages and blog posts, and ensure consistency with branding and messaging.", 1, '2023-07-01');


INSERT INTO project_requirement (project_id, skill_id) 
VALUES
(9001, 1),(9001, 7),(9001, 8),(9001, 11),(9002, 2),(9002, 3),(9002, 4),(9002, 7),
(9002, 11),(9002, 12),(9002, 13),(9003, 1),(9003, 2),(9003, 7),(9003, 10),(9003, 12),
(9004, 3),(9004, 6),(9004, 12),(9004, 13),(9005, 2),(9005,3),(9005, 4),(9005, 7),
(9005, 11),(9005, 12),(9005, 10),(9006, 1),(9006, 7),(9006, 8),(9006, 9),(9006, 11),
(9007, 2),(9007, 5),(9007, 7),(9007, 10),(9007, 13),(9008, 1),(9008, 7),(9008, 8),
(9008, 9),(9008, 10),(9009, 2),(9009, 7),(9009, 8),(9009, 9),(9009, 11),(9009, 13),
(9010, 1),(9010, 2),(9010, 8),(9010, 9),(9011, 1),(9011, 2),(9011, 3),(9011, 4),
(9011, 10),(9011, 11),(9011, 12),(9012, 1),(9012, 2),(9012, 4),(9012, 7),(9012, 8),
(9012, 11),(9012, 13),(9013, 2),(9013, 2),(9013, 3),(9013, 4),(9013, 7),(9013, 11),
(9013, 12),(9014, 2),(9014, 4),(9014, 7),(9014, 8),(9014, 9),(9014, 10),(9015, 2),
(9015, 3),(9015, 4),(9015, 5),(9015, 7),(9015, 8),(9015, 9),(9016, 1),(9016, 7),
(9016, 8),(9016, 9),(9016, 10),(9016, 11),(9017, 2),(9017, 5),(9017, 6),(9017, 7),
(9017, 13),(9018, 2),(9018, 4),(9018, 7),(9018, 8),(9018, 10),(9018, 11),(9019, 2),
(9019, 5),(9019, 6),(9019, 7),(9019, 10),(9019, 11),(9019, 12),(9019, 13),(9020, 1),
(9020, 2),(9020, 5),(9020, 7),(9020, 10),(9020, 12),(9021, 2),(9021, 3),(9021, 4),
(9021, 7),(9021, 8),(9021, 10),(9021, 11),(9021, 12),(9022, 2),(9022, 5),(9022, 6),
(9022, 7),(9022, 10),(9022, 13),(9023, 2),(9023, 3),(9023, 4),(9023, 8),(9023, 8),
(9023, 11),(9023, 12),(9024, 2),(9024,3),(9024, 4),(9024, 7),(9024, 10),(9024, 11),(9024, 12);


INSERT INTO student_skills (student_id, skill_id)
VALUES
(1001, 1), (1001, 2), (1001, 3), (1001, 4), (1001, 7), (1001, 8), (1001, 11), (1002, 2), (1002, 3), (1002, 4), (1002, 7), (1002, 10), 
(1003, 2), (1003, 4), (1003, 7), (1003, 11), (1004, 2), (1004, 3), (1004, 4), (1004, 7), (1004, 10), (1005, 2), 
(1005, 3), (1005, 4), (1005, 7), (1006, 2), (1006, 4), (1006, 5), (1006, 7), (1006, 11), (1007, 2), (1007, 3), 
(1007, 4), (1007, 7), (1007, 9), (1007, 13), (1008, 2), (1008, 3), (1008, 4), (1008, 7), (1008, 12), (1009, 2), 
(1009, 3), (1009, 4), (1009, 7), (1009, 11),(1010, 2), (1010, 3), (1010, 4), (1010, 7), (1010, 8), (1010, 11), 
(1010, 12), (1011, 2), (1011, 4), (1011, 7), (1011, 8), (1011, 9), (1012, 2), (1012, 3), (1012, 5), (1012, 6), 
(1012, 11), (1013, 2), (1013, 3), (1013, 4), (1013, 7), (1013, 10), (1014, 2), (1014, 3), (1014, 4), (1014, 7), 
(1014, 11), (1015, 2), (1015, 3), (1015, 4), (1015, 7), (1015, 12), (1016, 2), (1016, 3), (1016, 4), (1016, 7),
(1016, 13), (1017, 2), (1017, 4), (1017, 7), (1017, 8), (1017, 9), (1018, 2), (1018, 3), (1018, 4), (1018, 7), 
(1018, 11), (1019, 2), (1019, 3), (1019, 4), (1019, 7), (1019, 12), (1020, 2), (1020, 3), (1020, 4), (1020, 7), 
(1020, 13), (1021, 2), (1021, 5), (1021, 6), (1021, 8), (1021, 10), (1022, 2), (1022, 4), (1022, 6), (1022, 7), 
(1022, 10), (1023, 2), (1023, 3), (1023, 4), (1023, 6), (1023, 9), (1024, 2), (1024, 4), (1024, 5), (1024, 6), 
(1024, 11), (1025, 2), (1025, 3), (1025, 5), (1025, 8), (1025, 12), (1026, 2), (1026, 3), (1026, 5), (1026, 6), 
(1026, 13), (1027, 2), (1027, 3), (1027, 4), (1027, 6), (1027, 10), (1028, 2), (1028, 4), (1028, 5), (1028, 6),
(1028, 12), (1029, 2), (1029, 3), (1029, 5), (1029, 6), (1029, 11), (1030, 2), (1030, 3), (1030, 4), (1030, 5), 
(1030, 7),(1031, 2), (1031, 3), (1031, 6), (1032, 2), (1032, 4), (1032, 7), (1033, 1), (1033, 3), (1033, 8), 
(1034, 2), (1034, 3), (1034, 11), (1035, 4), (1035, 6), (1035, 10), (1036, 2), (1036, 4), (1036, 13), (1037, 2), 
(1037, 3), (1037, 9), (1038, 1), (1038, 7), (1038, 12), (1039, 2), (1039, 5), (1039, 6), (1040, 3), (1040, 7),
(1040, 10), (1041, 1), (1041, 3), (1041, 5), (1042, 2), (1042, 4), (1042, 7);


INSERT INTO wishlist (student_id, project_id, ranking, submission_status)
VALUES 
(1001, 9001, 1, 'Submitted'), (1001, 9010, 2, 'Submitted'), (1001, 9015, 3, 'Submitted'), (1001, 9022, 4, 'Submitted'),
(1002, 9003, 1, 'Drafted'), (1002, 9006, 2, 'Drafted'), (1002, 9021, 3, 'Drafted'), (1002, 9010, 4, 'Drafted'),
(1003, 9012, 1, 'Drafted'), (1003, 9022, 2, 'Drafted'), (1003, 9015, 3, 'Drafted'), (1003, 9008, 4, 'Drafted'),
(1004, 9004, 1, 'Drafted'), (1004, 9005, 2, 'Drafted'), (1004, 9020, 3, 'Drafted'), (1004, 9018, 4, 'Drafted'),
(1005, 9015, 1, 'Drafted'), (1005, 9017, 2, 'Drafted'), (1005, 9009, 3, 'Drafted'), (1005, 9002, 4, 'Drafted'),
(1006, 9021, 1, 'Drafted'), (1006, 9013, 2, 'Drafted'), (1006, 9023, 3, 'Drafted'), (1006, 9007, 4, 'Drafted'),
(1007, 9023, 1, 'Drafted'), (1007, 9008, 2, 'Drafted'), (1007, 9018, 3, 'Drafted'), (1007, 9021, 4, 'Drafted'),
(1008, 9017, 1, 'Drafted'), (1008, 9010, 2, 'Drafted'), (1008, 9001, 3, 'Drafted'), (1008, 9009, 4, 'Drafted'),
(1009, 9020, 1, 'Drafted'), (1009, 9003, 2, 'Drafted'), (1009, 9021, 3, 'Drafted'), (1009, 9019, 4, 'Drafted'),
(1010, 9022, 1, 'Drafted'), (1010, 9018, 2, 'Drafted'), (1010, 9024, 3, 'Drafted'), (1010, 9004, 4, 'Drafted'),
(1011, 9002, 1, 'Submitted'), (1011, 9008, 2, 'Submitted'), (1011, 9022, 3, 'Submitted'),
(1012, 9005, 1, 'Submitted'), (1012, 9012, 2, 'Submitted'), (1012, 9023, 3, 'Submitted'),
(1013, 9001, 1, 'Submitted'), (1013, 9013, 2, 'Submitted'), (1013, 9020, 3, 'Submitted'),
(1014, 9007, 1, 'Submitted'), (1014, 9014, 2, 'Submitted'), (1014, 9024, 3, 'Submitted'),
(1015, 9003, 1, 'Submitted'), (1015, 9016, 2, 'Submitted'), (1015, 9021, 3, 'Submitted'),
(1016, 9006, 1, 'Submitted'), (1016, 9015, 2, 'Submitted'), (1016, 9022, 3, 'Submitted'),
(1017, 9004, 1, 'Submitted'), (1017, 9017, 2, 'Submitted'), (1017, 9023, 3, 'Submitted'),
(1018, 9001, 1, 'Submitted'), (1018, 9014, 2, 'Submitted'), (1018, 9024, 3, 'Submitted'),
(1019, 9002, 1, 'Submitted'), (1019, 9016, 2, 'Submitted'), (1019, 9021, 3, 'Submitted'),
(1020, 9005, 1, 'Submitted'), (1020, 9013, 2, 'Submitted'), (1020, 9020, 3, 'Submitted'),
(1021, 9007, 1, 'Submitted'), (1021, 9012, 2, 'Submitted'), (1021, 9022, 3, 'Submitted'),
(1022, 9001, 1, 'Submitted'), (1022, 9009, 2, 'Submitted'), (1022, 9024, 3, 'Submitted'),
(1023, 9010, 1, 'Submitted'), (1023, 9015, 2, 'Submitted'), (1023, 9020, 3, 'Submitted'),
(1024, 9002, 1, 'Submitted'), (1024, 9012, 2, 'Submitted'), (1024, 9021, 3, 'Submitted'),
(1025, 9007, 1, 'Submitted'), (1025, 9011, 2, 'Submitted'), (1025, 9022, 3, 'Submitted'),
(1026, 9006, 1, 'Submitted'), (1026, 9008, 2, 'Submitted'), (1026, 9019, 3, 'Submitted'),
(1027, 9003, 1, 'Submitted'), (1027, 9013, 2, 'Submitted'), (1027, 9023, 3, 'Submitted'),
(1028, 9005, 1, 'Submitted'), (1028, 9010, 2, 'Submitted'), (1028, 9024, 3, 'Submitted'),
(1029, 9012, 1, 'Drafted'), (1029, 9014, 2, 'Drafted'), (1029, 9020, 3, 'Drafted'),
(1030, 9008, 1, 'Drafted'), (1030, 9010, 2, 'Drafted'), (1030, 9024, 3, 'Drafted'),
(1031, 9004, 1, 'Drafted'), (1031, 9015, 2, 'Drafted'), (1031, 9023, 3, 'Drafted'),
(1032, 9006, 1, 'Drafted'), (1032, 9012, 2, 'Drafted'), (1032, 9019, 3, 'Drafted'),
(1033, 9001, 1, 'Drafted'), (1033, 9005, 2, 'Drafted'), (1033, 9015, 3, 'Drafted'), (1033, 9022, 4, 'Drafted'), 
(1034, 9011, 1, 'Drafted'), (1034, 9019, 2, 'Drafted'), (1034, 9024, 3, 'Drafted'), (1034, 9002, 4, 'Drafted'), 
(1035, 9015, 1, 'Drafted'), (1035, 9018, 2, 'Drafted'), (1035, 9008, 3, 'Drafted'), (1035, 9021, 4, 'Drafted'),
(1036, 9024, 1, 'Drafted'), (1036, 9009, 2, 'Drafted'), (1036, 9013, 3, 'Drafted'), (1036, 9001, 4, 'Drafted'), 
(1037, 9012, 1, 'Drafted'), (1037, 9022, 2, 'Drafted'), (1037, 9017, 3, 'Drafted'), (1037, 9007, 4, 'Drafted'), 
(1038, 9002, 1, 'Drafted'), (1038, 9023, 2, 'Drafted'), (1038, 9005, 3, 'Drafted'), (1038, 9020, 4, 'Drafted'), 
(1039, 9018, 1, 'Drafted'), (1039, 9024, 2, 'Drafted'), (1039, 9009, 3, 'Drafted'), (1039, 9012, 4, 'Drafted'), 
(1040, 9014, 1, 'Drafted'), (1040, 9011, 2, 'Drafted'), (1040, 9001, 3, 'Drafted'), (1040, 9023, 4, 'Drafted'), 
(1041, 9007, 1, 'Drafted'), (1041, 9016, 2, 'Drafted'), (1041, 9022, 3, 'Drafted'), (1041, 9005, 4, 'Drafted'), 
(1042, 9010, 1, 'Drafted'), (1042, 9019, 2, 'Drafted'), (1042, 9006, 3, 'Drafted'), (1042, 9021, 4, 'Drafted');



INSERT INTO placement(student_id, project_id, pl_status) 
VALUES
(1001, 9001, 'Matched'), (1011, 9008, 'Matched');








