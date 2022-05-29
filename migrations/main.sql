-- define postgres chema"
SET search_path to public;

--Сreate table university"
-- university_pk marked as PK to university_id"
CREATE TABLE university(
    university_id integer NOT NULL,
    university_name varchar(255),
    logo varchar(255),
    CONSTRAINT university_pk PRIMARY KEY (university_id));

-- Create sequence university_id_seq"
CREATE SEQUENCE IF NOT EXISTS university_id_seq AS bigint
START WITH 1 INCREMENT BY 1;

ALTER TABLE university ALTER COLUMN university_id SET DEFAULT
nextval('university_id_seq');

-- Сreate table faculty
-- faculty_pk marked as PK to faculty_id"
CREATE TABLE faculty(
    faculty_id integer NOT NULL,
    name varchar(255),
    shortname varchar(20),
    main_email varchar(50),
    hostel_email varchar(50),
    university_id integer,
    CONSTRAINT faculty_pk PRIMARY KEY (faculty_id));

-- Create sequence faculty_id_seq
CREATE SEQUENCE IF NOT EXISTS faculty_id_seq AS bigint
START WITH 1 INCREMENT BY 1;

-- Link sequnce to column faculty_id
ALTER TABLE faculty ALTER COLUMN faculty_id SET DEFAULT
nextval('faculty_id_seq');

-- Mark faculty_university_fk as a FK to university_id"
ALTER TABLE faculty ADD CONSTRAINT faculty_university_fk FOREIGN KEY (university_id)
REFERENCES university (university_id) 
MATCH FULL
ON DELETE CASCADE 
ON UPDATE CASCADE;


-- Create table student"
-- student_pk marked as PK to faculty_id"
CREATE TABLE student (
    student_id integer NOT NULL,
    full_name varchar(255),
    telephone_number varchar(255),
    faculty_id integer,
    user_id integer,
    CONSTRAINT student_pk PRIMARY KEY(student_id));


-- Create sequence student_id_seq
CREATE SEQUENCE IF NOT EXISTS student_id_seq AS bigint
START WITH 1 INCREMENT BY 1;

-- Link sequence to column student_id
ALTER TABLE student ALTER COLUMN student_id SET DEFAULT
nextval('student_id_seq');

-- Mark faculty_id as FK to faculty(faculty_id)"
ALTER TABLE student ADD CONSTRAINT student_faculty_fk FOREIGN KEY (faculty_id)
REFERENCES faculty(faculty_id)
MATCH FULL
ON DELETE CASCADE
ON UPDATE CASCADE; 

-- Mark student_user_fk as FK to user(user_id)"
ALTER TABLE student ADD CONSTRAINT student_user_fk FOREIGN KEY (user_id)
REFERENCES "user"(user_id)
MATCH FULL
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Create table user
CREATE TABLE "user"(
    user_id integer NOT NULL,
    login varchar(50),
    password varchar(50),
    last_visit timestamp,
    email varchar(100),
    role_id integer,
    is_active BOOLEAN DEFAULT FALSE,
    CONSTRAINT user_pk PRIMARY KEY(user_id));

-- Create sequence user_id_seq"
CREATE SEQUENCE IF NOT EXISTS user_id_seq AS bigint
START WITH 1 INCREMENT BY 1;

-- Link sequence to column user_id_seq
ALTER TABLE "user" ALTER COLUMN user_id SET DEFAULT
nextval('user_id_seq');

-- Mark user_faculty_fk as FK to faculty(faculty_id)"
ALTER TABLE user ADD CONSTRAINT user_faculty_fk FOREIGN KEY(faculty_id)
REFERENCES faculty(faculty_id)
MATCH FULL
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Create table role"
CREATE TABLE role(
    role_id integer,
    role_name varchar(50),
    CONSTRAINT role_pk PRIMARY KEY(role_id));

-- Create sequence role_id_seq"
CREATE SEQUENCE IF NOT EXISTS role_id_seq AS bigint
START WITH 1 INCREMENT BY 1;

-- Link sequence to column role_id_seq
ALTER TABLE role ALTER COLUMN role_id SET DEFAULT
nextval('role_id_seq');

-- Mark user_role_fk as FK to role(role_id)"
ALTER TABLE "user" ADD CONSTRAINT user_role_fk FOREIGN KEY(role_id)
REFERENCES role(role_id)
MATCH FULL
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Create table actions"
CREATE TABLE action(
    role_id integer, 
    action_name varchar(50),
    action_id integer,
    CONSTRAINT action_pk PRIMARY KEY(action_id));

-- Create sequence action_id_seq"
CREATE SEQUENCE IF NOT EXISTS action_id_seq AS bigint
START WITH 1 INCREMENT BY 1;

-- Link sequence to column action_id_seq
ALTER TABLE action ALTER COLUMN action_id SET DEFAULT
nextval('action_id_seq');

-- Mark action_role_fk as FK to action(role(id)"
ALTER TABLE action ADD CONSTRAINT action_role_fk FOREIGN KEY(role_id)
REFERENCES role(role_id)
MATCH FULL
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Create table user_faculty
CREATE TABLE user_faculty(
    user_id integer NOT NULL,
    faculty_id integer NOT NULL,
    CONSTRAINT user_faculty_pk PRIMARY KEY(user_id, faculty_id));

--Mark user_faculty as FK to user(user_id)
ALTER TABLE user_faculty ADD CONSTRAINT user_faculty_user_fk FOREIGN KEY(user_id)
REFERENCES "user"(user_id)
MATCH FULL
ON DELETE CASCADE
ON UPDATE CASCADE; 

-- Mark user_faculty as FK faculty(faculty_id)
ALTER TABLE user_faculty ADD CONSTRAINT user_faculty_faculty_fk FOREIGN KEY(faculty_id)
REFERENCES faculty(faculty_id)
MATCH FULL
ON DELETE CASCADE
ON UPDATE CASCADE;
