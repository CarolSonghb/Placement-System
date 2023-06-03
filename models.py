import connect
import mysql.connector
from flask_login import UserMixin
import random
from flask_paginate import Pagination, get_page_args, get_page_parameter
from flask import request

dbconn = None


def get_cursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(
            user=connect.dbuser,
            password=connect.dbpass, host=connect.dbhost,
            database=connect.dbname, autocommit=True,
        )
        dbconn = connection.cursor(dictionary=True)
        return dbconn
    else:
        return dbconn


def run_data(sql, para=None, fetch=None):
    cur = get_cursor()
    if para:
        cur.execute(sql, para)
    else:
        cur.execute(sql,)

    if fetch == 1:
        result = cur.fetchone()
        return result
    elif fetch == 2:
        result = cur.fetchall()
        return result
    else:
        return 'no need to print'


def colprint():
    cur = get_cursor()
    column_print = [desc[0] for desc in cur.description]
    print(column_print)
    return column_print


def generate_randomint():
    seeds = "1234567890"
    random_int = []
    for i in range(4):
        random_int.append(random.choice(seeds))
    return "".join(random_int)


# create pagination func - simon
def paginate_func(content, per_page=10):
    per_page = per_page
    page = request.args.get(get_page_parameter(), type=int, default=1)

    start = (page-1) * per_page
    end = start + per_page

    pagination = Pagination(page=page, total=len(content), per_page=per_page,
                            outer_window=0, css_framework='bootstrap5')

    return content[start:end], pagination


class User:
    def __init__(self, user_name, password_new=None, database_path=None):
        self.user_name = user_name
        self.password_new = password_new

    def check_password(self):
        sql = f"select password,role from user where user_name = '{self.user_name}'"
        return run_data(sql, fetch=1)

    def get_user(self):
        sql = f"select * from student where user_name = '{self.user_name}'"
        return run_data(sql, fetch=1)

    def update_password(self):
        sql = "update user set password = %s where user_name = %s;"
        para = (self.password_new, self.user_name)
        run_data(sql, para)

    def add_user(self):
        sql = '''INSERT INTO user(user_name, password, role) VALUES(%s,%s,%s)'''
        para = (self.user_name, self.password_new, 'student')
        run_data(sql, para)

    def get_avatar(self, user_name):
        sql = '''select link from user where user_name = %s'''
        para = (user_name,)
        return run_data(sql, para, fetch=2)

    def update_avatar(self, user_name, database_path):
        sql = '''update user set link = %s where User_name = %s'''
        para = (database_path, user_name)
        run_data(sql, para)


class Student:
    def __init__(self, user_name, student_id=None, student_update=None):
        self.user_name = user_name
        self.student_id = student_id
        self.student_update = student_update

    def get_student(self):
        sql = ''' SELECT s.* , GROUP_CONCAT(sk.details) AS skills FROM student AS s
                    JOIN student_skills AS ss ON s.student_id = ss.student_id
                    JOIN skills AS sk ON ss.skill_id = sk.skill_id
                    WHERE s.user_name = %s
                    GROUP BY s.student_id
                    ;'''
        para = (self.user_name,)
        return run_data(sql, para, fetch=1)

    def get_student_skills(self):
        sql = ''' SELECT s.student_id, s.user_name, s.first_name, s.last_name , GROUP_CONCAT(sk.details) FROM student AS s
                JOIN student_skills AS ss ON s.student_id = ss.student_id
                JOIN skills AS sk ON ss.skill_id = sk.skill_id WHERE s.user_name = %s
                GROUP BY s.student_id;'''
        para = (self.user_name,)
        return run_data(sql, para, fetch=1)

    def get_placement(self):
        sql = ''' 
        SELECT p.student_id, p.pl_status, p.project_id, CONCAT(m.first_name,' ',m.last_name) AS mentor_name,
        pj.start_date, m.company_name, pj.project_title, GROUP_CONCAT(s.details separator ',') AS skills, 
        pj.project_summary
        FROM placement AS p
        JOIN project AS pj ON p.project_id = pj.project_id
        JOIN mentor AS m ON pj.mentor_id = m.mentor_id
        JOIN project_requirement AS pr ON p.project_id = pr.project_id
        JOIN skills AS s ON pr.skill_id = s.skill_id 
        WHERE p.student_id = %s
        GROUP BY p.student_id, p.project_id, p.pl_status;'''
        para = (self.student_id,)
        return run_data(sql, para, fetch=2)

    def get_wishlist(self):
        sql = '''
        SELECT w.ranking, w.project_id, CONCAT(m.first_name,' ',m.last_name) as mentor_name, w.submission_status, m.company_name,
        p.project_title, p.project_summary as project_summary
        from wishlist as w
            join project as p ON w.project_id = p.project_id
	            join mentor as m on p.mentor_id = m.mentor_id where w.student_id = %s and w.submission_status <> 'Submitted';'''
        para = (self.student_id,)
        return run_data(sql, para, fetch=2)

    def wishlist_status(self):
        sql = '''SELECT w.ranking, w.project_id, CONCAT(m.first_name,' ',m.last_name) as mentor_name, w.submission_status, m.company_name,
        p.project_title, p.project_summary as project_summary
        from wishlist as w
            join project as p ON w.project_id = p.project_id
	            join mentor as m on p.mentor_id = m.mentor_id where w.student_id = %s and
                w.submission_status = 'Submitted';'''
        para = (self.student_id,)
        result = run_data(sql, para, fetch=2)
        if result:
            return result
        else:
            return 0

    def update(self, student_update):
        sql = '''UPDATE student SET first_name = %s, last_name = %s, preferred_name = %s, email = %s, phone = %s, need_project = %s, 
        currently_enrolled = %s, location = %s, semester_to_place = %s, cv_link = %s WHERE student_id = %s'''
        para = (student_update['first_name'], student_update['last_name'], student_update['preferred_name'], student_update['email'],
                student_update['phone'], student_update['need_project'], student_update['currently_enrolled'], student_update['location'],
                student_update['semester_to_place'], student_update['cv_link'], student_update['student_id'])
        run_data(sql, para)

    def cv_link(self):
        sql = f'''SELECT cv_link FROM student where user_name = '{self.user_name}' '''
        return run_data(sql, fetch=1)


class Skills:
    def __init__(self, data=None):
        self.data = data

    def all_skills(self):
        sql = '''SELECT * FROM skills'''
        return run_data(sql, fetch=2)


class NewStudent:
    def __init__(self, result):
        self.result = result

    def add_student(self, result):
        sql = ''' INSERT INTO student(student_id, user_name, first_name, last_name, preferred_name, email, phone, 
                location, need_project, currently_enrolled, semester_to_place, cv_link)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        para = (result['student_id'], result['user_name'], result['first_name'], result['last_name'], result['preferred_name'],
                result['email'], result['phone'], result['location'], result['need_project'],
                result['currently_enrolled'], result['semester_to_place'], result['cv_link'])

        run_data(sql, para)

    def add_student_skill(self, result):
        sql = '''INSERT INTO student_skills(student_id,skill_id) VALUES(%s,%s);'''
        for skill in result['skills']:
            para = (result['student_id'], skill)
            run_data(sql, para)
        return 'Success'


class Projects:
    def __init__(self, project_id=None, data=None, student_id=None):
        self.project_id = project_id
        self.data = data
        self.student_id = student_id

    def all_projects(self):
        sql = '''
        select p.project_id, CONCAT(m.first_name,' ',last_name) AS mentor_name, m.company_name, m.industry, 
        m.location, p.project_title, p.start_date, GROUP_CONCAT(s.details separator ',') AS 'skills', p.project_summary
        FROM project AS p
            JOIN mentor AS m ON p.mentor_id = m.mentor_id
                JOIN project_requirement AS pr ON p.project_id = pr.project_id
                    JOIN skills AS s ON pr.skill_id = s.skill_id GROUP BY p.project_id;'''

        return run_data(sql, fetch=2)

    def filter_projects(self, data):
        # def inner():
        base_sql = f'''
                select p.project_id, CONCAT(m.first_name,' ',last_name) AS mentor_name, m.company_name, m.industry, 
                            m.location, p.project_title, p.start_date, GROUP_CONCAT(s.details separator ',') AS 'skills', p.project_summary
                            FROM project AS p
                                JOIN mentor AS m ON p.mentor_id = m.mentor_id
                                    JOIN project_requirement AS pr ON p.project_id = pr.project_id
                                        JOIN skills AS s ON pr.skill_id = s.skill_id GROUP BY p.project_id HAVING 1=1 '''

        if data['location']:
            con_sql = f"and LOWER(m.location) like LOWER('%{data['location']}%') "
            base_sql += con_sql
        if data['name']:
            con_sql = f"and LOWER(m.company_name) like LOWER('%{data['name']}%') "
            base_sql += con_sql
        if data['industry']:
            con_sql = f"and LOWER(m.industry) like LOWER('%{data['industry']}%') "
            base_sql += con_sql
        if data['skills']:
            con_sql = f"and LOWER(skills) like LOWER('%{data['skills']}%') "
            base_sql += con_sql

        # if data['project_title']:
        #     con_sql = f"and LOWER(p.project_title) like LOWER('%{data['project_title']}%') "

        # if data['project_summary']:
        #     con_sql = f"and LOWER(p.project_summary) like LOWER('%{data['project_summary']}%') "
        # print(sql)

        return run_data(base_sql, fetch=2)

        # return inner

    def projects_details(self, project_id):
        sql = '''
        select p.project_id, CONCAT(m.first_name,' ',last_name) AS mentor_name, m.company_name, m.industry, 
        m.location, p.project_title, p.start_date, GROUP_CONCAT(s.details separator ',') AS 'skills', p.project_summary
        FROM project AS p
            JOIN mentor AS m ON p.mentor_id = m.mentor_id
                JOIN project_requirement AS pr ON p.project_id = pr.project_id
                    JOIN skills AS s ON pr.skill_id = s.skill_id where p.project_id = %s GROUP BY p.project_id;'''
        para = (project_id,)
        return run_data(sql, para=para, fetch=1)

    def all_locations(self):
        sql = '''select location from mentor group by location;'''
        return run_data(sql, fetch=2)

    def update_project(self, data):
        sql = '''
        update project set project_title =%s, project_summary=%s, place_num=%s, start_date=%s where project_id=%s;
        '''
        para = (data['project_title'], data['project_sum'], data['place_num'],
                data['project_date'], data['project_id'])
        run_data(sql, para)
        return 'success'

    def selected_projects(self, student_id):
        sql = f'''select project_id from wishlist where student_id = {student_id};'''
        selected_project_list = run_data(sql, fetch=2)
        # print(selected_project_list)
        selected_project = []
        if selected_project_list:
            for select in selected_project_list:
                selected_project.append(select['project_id'])
            selected_project = selected_project
        return selected_project

    def projects_submitted(self, student_id):
        sql = '''select * from wishlist where student_id = %s and submission_status = "Submitted";'''
        para = (student_id,)
        result = run_data(sql, para, fetch=2)
        if result:
            return 1
        else:
            return 0

    def students_interested(self, project_id):
        sql = '''SELECT w.student_id, w.project_id, w.ranking, w.submission_status,
                s.first_name, s.last_name, s.email, s.phone, s.location, s.semester_to_place,
                pl.pl_status, GROUP_CONCAT(sk.details) AS skills 
                
                FROM wishlist AS w
                JOIN student AS s ON w.student_id = s.student_id
                JOIN student_skills AS ss ON s.student_id = ss.student_id
                JOIN skills AS sk ON ss.skill_id=sk.skill_id
                LEFT JOIN placement AS pl ON w.student_id = pl.student_id
                WHERE s.currently_enrolled="1" AND s.semester_to_place="2" AND s.need_project="1"
                AND w.project_id= %s AND w.student_id NOT IN ( SELECT student_id FROM placement WHERE project_id = %s)
                GROUP BY w.student_id, w.project_id,w.ranking, w.submission_status,
                s.first_name, s.last_name, s.email, s.phone, s.semester_to_place,pl.pl_status
                ORDER BY w.ranking ASC;'''
        para = (project_id, project_id)
        return run_data(sql, para, fetch=2)

    def skills_required(self, project_id):
        sql = '''SELECT p.project_id, p.project_title, p.start_date, GROUP_CONCAT(s.details) AS skills ,
                m.first_name, m.last_name, m.location, m.company_name, m.industry
                FROM project AS p
                JOIN project_requirement AS pr ON p.project_id = pr.project_id
                JOIN skills AS s ON pr.skill_id = s.skill_id
                JOIN mentor AS m ON p.mentor_id = m.mentor_id
                WHERE pr.project_id = %s
                GROUP BY p.project_id;'''
        para = (project_id,)
        return run_data(sql, para, fetch=1)

# 如何添加validate 如果location 匹配不到
    def match_students(self, project_id):
        sql = '''SELECT ss.student_id, s.first_name, s.last_name,s.email,s.phone,s.location,
                GROUP_CONCAT(sk.details) AS student_skills, COUNT(*) AS skills_matched, 
                (SELECT m.mentor_id FROM project WHERE project_id = %s) AS mentor_id
                FROM 
                student_skills AS ss 
                JOIN student AS s ON ss.student_id = s.student_id 
                JOIN skills AS sk ON ss.skill_id = sk.skill_id 
                JOIN mentor AS m ON m.mentor_id = (SELECT mentor_id FROM project WHERE project_id = %s)
                WHERE 
                ss.skill_id IN (SELECT skill_id FROM project_requirement WHERE project_id = %s)
                AND s.location = m.location
                AND s.currently_enrolled="1" AND s.semester_to_place="2" AND s.need_project="1"
                And ss.student_id not in (select student_id from placement where pl_status = "Confirmed")
                GROUP BY ss.student_id, m.mentor_id
                ORDER BY skills_matched DESC;'''
        para = (project_id, project_id, project_id)

        if not run_data(sql, para, fetch=2):
            sql = '''SELECT ss.student_id, s.first_name, s.last_name,s.email,s.phone,s.location,
                    GROUP_CONCAT(sk.details) AS student_skills, COUNT(*) AS skills_matched, 
                    (SELECT m.mentor_id FROM project WHERE project_id = %s) AS mentor_id
                    FROM 
                    student_skills AS ss 
                    JOIN student AS s ON ss.student_id = s.student_id 
                    JOIN skills AS sk ON ss.skill_id = sk.skill_id 
                    JOIN mentor AS m ON m.mentor_id = (SELECT mentor_id FROM project WHERE project_id = %s)
                    WHERE 
                    ss.skill_id IN (SELECT skill_id FROM project_requirement WHERE project_id = %s)
                    AND s.currently_enrolled="1" AND s.semester_to_place="2" AND s.need_project="1"
                    And ss.student_id not in (select student_id from placement where pl_status = "Confirmed")
                    GROUP BY ss.student_id, m.mentor_id
                    ORDER BY skills_matched DESC;'''
            return run_data(sql, para, fetch=2)[:6]
        return run_data(sql, para, fetch=2)[:6]

    def skill_match_number(self, project_id):
        sql = '''select distinct  w.project_id, ss.student_id, COUNT(ss.skill_id) AS skills_matched
                    from student_skills as ss
                    join wishlist as w on ss.student_id = w.student_id
                    join project_requirement as pr on w.project_id = pr.project_id and ss.skill_id = pr.skill_id
                    where w.project_id = %s and ss.student_id NOT IN ( SELECT student_id FROM placement WHERE project_id = %s)
                    group by student_id;'''
        para = (project_id, project_id)
        return run_data(sql, para, fetch=2)

    def available_slots(self, project_id):
        sql = '''SELECT p.project_id, students_placed, p.place_num, (p.place_num - ifnull(students_placed, 0)) AS available_slots
                FROM project AS p LEFT JOIN (SELECT project_id, COUNT(*) AS students_placed FROM placement WHERE pl_status= 'Confirmed' 
                GROUP BY project_id) AS pl ON p.project_id = pl.project_id
                WHERE p.project_id= %s; '''
        para = (project_id,)
        return run_data(sql, para, fetch=1)

    def match_count(self, project_id):
        sql = '''SELECT pj.project_id, COUNT(DISTINCT p.student_id) AS student_count, pj.place_num
                FROM project as pj
                left join placement as p on pj.project_id =p.project_id 
                WHERE pj.project_id = %s'''
        para = (project_id,)
        return run_data(sql, para, fetch=1)

    def confirm_count(self, project_id):
        sql = '''
            SELECT IFNULL(pj.project_id, %s) AS project_id, COUNT(DISTINCT p.student_id) AS student_count,
                    (SELECT place_num FROM project WHERE project_id = %s) AS place_num
                FROM project AS pj
                LEFT JOIN placement AS p ON pj.project_id = p.project_id
                WHERE pj.project_id = %s AND p.pl_status = 'Confirmed';'''
        para = (project_id, project_id, project_id)
        return run_data(sql, para, fetch=1)


# danger ! only for updating the project by mentor

    def remove_skills(self, data):
        sql = '''DELETE FROM project_requirement WHERE project_id=%s;'''
        para = (data['project_id'],)
        run_data(sql, para)


class WishiList:
    def __init__(self, project_id=None, student_id=None, ranking=None):
        self.project_id = project_id
        self.student_id = student_id
        self.ranking = ranking

    def remove_project(self, project_id, student_id):
        sql = '''DELETE FROM wishlist WHERE project_id=%s AND student_id=%s;'''
        para = (project_id, student_id)
        run_data(sql, para)

    def add_project(self, project_id, student_id):
        sql = '''INSERT INTO wishlist (project_id,student_id,ranking,submission_status) VALUES (%s,%s,%s,%s)'''
        para = (project_id, student_id, 1, 'Drafted')
        run_data(sql, para)

    def update_project(self, project_id, student_id, ranking):
        sql = '''update wishlist set ranking = %s, submission_status = 'Submitted' where project_id = %s and student_id = %s;'''
        para = (ranking, project_id, student_id)
        run_data(sql, para)


class Mentor:
    def __init__(self, user_name, mentor_id=None, project_id=None, student_id=None, status=None, data=None, mentor_update=None):
        self.user_name = user_name
        self.mentor_id = mentor_id
        self.project_id = project_id
        self.student_id = student_id
        self.status = status
        self.data = data
        self.mentor_update = mentor_update

    def get_mentor(self):
        sql = '''SELECT * , CONCAT(first_name,' ',last_name) AS name FROM mentor WHERE user_name = %s;'''
        para = (self.user_name,)
        return run_data(sql, para, fetch=1)

    def update(self, mentor_update):
        sql = '''UPDATE mentor SET first_name = %s , last_name = %s , email = %s , phone = %s , location = %s WHERE mentor_id = %s'''
        para = (mentor_update['first_name'], mentor_update['last_name'], mentor_update['email'], mentor_update['phone'],
                mentor_update['location'], mentor_update['mentor_id'])
        run_data(sql, para)

    def get_mentor_id(self):
        sql = '''SELECT mentor_id FROM mentor WHERE user_name = %s;'''
        para = (self.user_name,)
        return run_data(sql, para, fetch=1)

    def get_project_id(self):
        sql = '''SELECT project_id FROM project WHERE mentor_id = %s;'''
        para = (self.mentor_id,)
        return run_data(sql, para, fetch=2)

    def mentor_projects(self):
        sql = '''SELECT p.* ,GROUP_CONCAT(sk.details separator ',') AS 'skills', m.location, m.industry, m.company_name
            FROM mentor AS m 
            JOIN project AS p ON m.mentor_id = p.mentor_id
            LEFT JOIN project_requirement AS pr ON p.project_id = pr.project_id
            LEFT JOIN skills AS sk ON pr.skill_id = sk.skill_id
            WHERE m.mentor_id = %s GROUP BY p.project_id ;'''
        para = (self.mentor_id,)
        return run_data(sql, para, fetch=2)

    def get_placement(self):
        sql = '''SELECT pl.student_id, s.first_name, s.last_name, s.email, s.phone, s.location, 
                s.cv_link, pl.project_id,  p.project_title, p.start_date,  m.mentor_id,  pl.pl_status,  GROUP_CONCAT(sk.details separator ',') AS 'skills'
                FROM placement AS pl
                JOIN student AS s ON pl.student_id = s.student_id 
                JOIN student_skills AS ss ON s.student_id = ss.student_id 
                JOIN skills AS sk ON ss.skill_id = sk.skill_id 
                JOIN project AS p ON pl.project_id = p.project_id 
                JOIN mentor AS m ON p.mentor_id = m.mentor_id
                WHERE p.mentor_id = %s
                GROUP BY pl.student_id, pl.project_id,pl.pl_status;'''
        para = (self.mentor_id,)
        return run_data(sql, para, fetch=2)

    def update_placement_status(self, data):
        sql = '''UPDATE placement SET pl_status = %s WHERE student_id = %s AND project_id = %s;'''
        para = (data['status'], data['student_id'], data['project_id'])
        run_data(sql, para)

    def new_placement(self, data):
        sql = '''INSERT INTO placement (student_id, project_id, pl_status) VALUES (%s,%s,%s);'''
        para = (data['student_id'], data['project_id'], data['status'])
        run_data(sql, para)

    def matched_students(self):
        sql = '''SELECT pl.student_id, pl.pl_status, s.first_name, s.last_name, s.email, s.phone, s.location, 
                s.cv_link, pl.project_id,  p.project_title, p.start_date,  m.mentor_id,  GROUP_CONCAT(sk.details separator ', ') AS 'skills'
                FROM placement AS pl
                JOIN student AS s ON pl.student_id = s.student_id 
                JOIN student_skills AS ss ON s.student_id = ss.student_id 
                JOIN skills AS sk ON ss.skill_id = sk.skill_id 
                JOIN project AS p ON pl.project_id = p.project_id 
                JOIN mentor AS m ON p.mentor_id = m.mentor_id
                WHERE p.mentor_id = %s
                AND pl_status IN ('Matched', 'Interviewed', 'Confirmed')
                GROUP BY pl.student_id, pl.pl_status, pl.project_id;'''
        para = (self.mentor_id,)
        return run_data(sql, para, fetch=2)

    def matched_students_withajax(self):
        sql = '''
        SELECT pl.student_id, pl.pl_status, s.first_name, s.last_name, s.email, s.phone, s.location, 
                s.cv_link, pl.project_id,  p.project_title, p.start_date,  m.mentor_id,  GROUP_CONCAT(sk.details separator ', ') AS 'skills'
                FROM placement AS pl
                JOIN student AS s ON pl.student_id = s.student_id 
                JOIN student_skills AS ss ON s.student_id = ss.student_id 
                JOIN skills AS sk ON ss.skill_id = sk.skill_id 
                JOIN project AS p ON pl.project_id = p.project_id 
                JOIN mentor AS m ON p.mentor_id = m.mentor_id
                WHERE p.mentor_id = %s and pl.project_id = %s
                AND pl_status IN ('Matched', 'Interviewed', 'Confirmed')
                GROUP BY pl.student_id, pl.pl_status, pl.project_id;'''
        para = (self.mentor_id, self.project_id)
        return run_data(sql, para, fetch=2)


class Staff:
    def __init__(self, user_name=None, staff_id=None, data=None, option=None):
        self.user_name = user_name
        self.staff_id = staff_id
        self.data = data
        self.option = option

    def get_staff(self):
        sql = '''select * from staff where user_name = %s '''
        para = (self.user_name,)
        return run_data(sql, para, fetch=1)

    def update_staff(self, data):
        sql = ''' update staff set first_name = %s, last_name = %s, email = %s, phone = %s where staff_id = %s; '''
        para = (data['first_name'], data['last_name'], data['email'],
                data['phone'], data['staff_id'])
        run_data(sql, para)

    def get_student_list(self):
        sql = '''SELECT s.student_id, pl.pl_status, pl.project_id, s.first_name, s.last_name, s.email, s.phone, s.location, s.currently_enrolled, 
                s.semester_to_place, s.need_project, s.cv_link, GROUP_CONCAT(sk.details) AS 'skills'
            FROM student AS s
            JOIN student_skills AS ss ON s.student_id = ss.student_id
            JOIN skills AS sk ON ss.skill_id = sk.skill_id
            LEFT JOIN placement AS pl ON ss.student_id = pl.student_id
            GROUP BY s.student_id, pl.pl_status, pl.project_id;'''
        return run_data(sql, fetch=2)

    def search_student_list(self, data):
        sql = '''SELECT s.student_id, pl.pl_status,pl.project_id, s.first_name, s.last_name, s.email, s.phone, s.location, s.currently_enrolled, 
                s.semester_to_place, s.need_project, s.cv_link, GROUP_CONCAT(sk.details) AS 'skills'
                FROM student AS s
                JOIN student_skills AS ss ON s.student_id = ss.student_id
                JOIN skills AS sk ON ss.skill_id = sk.skill_id
                LEFT JOIN placement AS pl ON ss.student_id = pl.student_id
                GROUP BY s.student_id , pl.pl_status having 1=1 '''

        if data['student_id']:
            con_sql = f"and LOWER(s.student_id) like LOWER('%{data['student_id']}%')"
            sql += con_sql
        if data['first_name']:
            con_sql = f"and LOWER(s.first_name) like LOWER('%{data['first_name']}%')"
            sql += con_sql
        if data['last_name']:
            con_sql = f"and LOWER(s.last_name) like LOWER('%{data['last_name']}%')"
            sql += con_sql
        if data.get('searchstatus'):
            con_sql = f"and pl.pl_status {data['searchstatus']}"
            sql += con_sql

        return run_data(sql, fetch=2)

    def student_class(self):
        sql = f'''
        SELECT s.student_id, pl.pl_status, MAX(pl.project_id) AS project_id, s.first_name, s.last_name, s.email, s.phone, s.location, s.currently_enrolled, 
                s.semester_to_place, s.need_project, s.cv_link, GROUP_CONCAT(sk.details) AS 'skills'
                FROM student AS s
                JOIN student_skills AS ss ON s.student_id = ss.student_id
                JOIN skills AS sk ON ss.skill_id = sk.skill_id
                LEFT JOIN placement AS pl ON ss.student_id = pl.student_id
                GROUP BY s.student_id , pl.pl_status
                having pl.pl_status {self.option}'''
        return run_data(sql, fetch=2)

    def get_student_need(self):
        sql = ''' SELECT s.student_id, pl.pl_status, s.first_name, s.last_name, s.email, s.phone, s.location, s.currently_enrolled, 
            s.semester_to_place, s.need_project, GROUP_CONCAT(sk.details) AS skills
            FROM student AS s
            JOIN student_skills AS ss ON s.student_id = ss.student_id
            JOIN skills AS sk ON ss.skill_id = sk.skill_id
            LEFT JOIN placement AS pl ON ss.student_id = pl.student_id
            WHERE s.need_project =1
            GROUP BY s.student_id, pl.pl_status ;'''
        return run_data(sql, fetch=2)

    def get_student_matched(self):
        sql = ''' SELECT s.student_id,s.first_name, s.last_name,  pl.pl_status, pl.project_id,
            pr.project_title, m.first_name AS "first", m.last_name AS "last", m.company_name,  m.industry
            FROM placement AS pl
            JOIN student as s ON pl.student_id = s.student_id
            JOIN project AS pr ON pl.project_id = pr.project_id
            JOIN mentor AS m ON pr.mentor_id = m.mentor_id;'''
        return run_data(sql, fetch=2)

    def get_project_list(self):
        sql = ''' SELECT m.mentor_id, m.company_name, m.industry, m.location, 
                p.project_id, p.project_title, p.project_summary, p.place_num, (SELECT COUNT(*) FROM placement 
                WHERE project_id = p.project_id AND pl_status = 'matched') AS "students_matched", 
               ( SELECT COUNT(*) FROM placement WHERE project_id = p.project_id AND pl_status = 'confirmed') AS 'confirmed',
                p.start_date FROM mentor AS m JOIN project AS p ON m.mentor_id = p.mentor_id
                LEFT JOIN placement AS pl ON p.project_id = pl.project_id
                GROUP BY m.mentor_id, p.project_id;'''
        return run_data(sql, fetch=2)

    def search_project_list(self, data):
        sql = ''' SELECT m.mentor_id, m.company_name, m.industry, m.location, 
        p.project_id, p.project_title, p.project_summary, p.place_num, (SELECT COUNT(*) FROM placement 
        WHERE project_id = p.project_id AND pl_status = 'matched') AS "students_matched", 
        ( SELECT COUNT(*) FROM placement WHERE project_id = p.project_id AND pl_status = 'confirmed') AS 'confirmed',
        p.start_date FROM mentor AS m JOIN project AS p ON m.mentor_id = p.mentor_id
        LEFT JOIN placement AS pl ON p.project_id = pl.project_id
        GROUP BY m.mentor_id, p.project_id having 1=1 '''

        if data['project_id']:
            con_sql = f"and LOWER(p.project_id) like LOWER('%{data['project_id']}%')"
            sql += con_sql
        if data['company_name']:
            con_sql = f"and LOWER(m.company_name) like LOWER('%{data['company_name']}%')"
            sql += con_sql
        if data['location']:
            con_sql = f"and LOWER(m.location) like LOWER('%{data['location']}%')"
            sql += con_sql
        if data['mentor_id']:
            con_sql = f"and LOWER(m.mentor_id) like LOWER('%{data['mentor_id']}%')"
            sql += con_sql

        return run_data(sql, fetch=2)

    def get_mentor_list(self):
        sql = ''' SELECT * FROM mentor;'''
        return run_data(sql, fetch=2)

    def search_mentor_list(self, data):
        sql = ''' SELECT * FROM mentor where 1=1 '''
        if data['mentor_id']:
            con_sql = f"and LOWER(mentor_id) like LOWER('%{data['mentor_id']}%')"
            sql += con_sql
        if data['company_name']:
            con_sql = f"and LOWER(company_name) like LOWER('%{data['company_name']}%')"
            sql += con_sql
        if data['first_name']:
            con_sql = f"and LOWER(first_name) like LOWER('%{data['first_name']}%')"
            sql += con_sql
        if data['last_name']:
            con_sql = f"and LOWER(last_name) like LOWER('%{data['last_name']}%')"
            sql += con_sql

        return run_data(sql, fetch=2)

    def palcement_report(self):
        sql = '''SELECT 
                (SELECT COUNT(CASE WHEN student.need_project = 1 AND student.semester_to_place = 2 THEN student.student_id END) 
                FROM student) AS students_needing_project_in_semester_2,
                (SELECT COUNT(CASE WHEN  student.semester_to_place = 2 THEN student.student_id END) FROM student) AS total_students,
                COUNT(project.place_num) AS available_placements,
                COUNT(DISTINCT CASE WHEN placement.pl_status = 'Matched' THEN placement.project_id END) AS potential_placements,
                COUNT(DISTINCT CASE WHEN placement.pl_status IN ('Matched', 'Interviewed') THEN placement.student_id END) AS student_matched,
                COUNT(DISTINCT CASE WHEN placement.pl_status = 'Confirmed' THEN placement.student_id END) AS student_confirmed,
                COUNT(DISTINCT project.project_id) AS total_projects,
                COUNT(DISTINCT mentor.mentor_id) AS total_mentors,
                COUNT(DISTINCT mentor.company_name) AS total_companies
            FROM 
                project
                LEFT JOIN mentor ON project.mentor_id = mentor.mentor_id
                LEFT JOIN project_requirement ON project.project_id = project_requirement.project_id
                LEFT JOIN skills ON project_requirement.skill_id = skills.skill_id
                LEFT JOIN placement ON project.project_id = placement.project_id;
            '''
        return run_data(sql, fetch=1)

    def industry_category(self):
        sql = '''SELECT COUNT(p.project_id) AS Projects, industry, Sum(p.place_num) AS "Placement Available"
                FROM mentor AS m LEFT JOIN project AS p ON m.mentor_id = p.mentor_id GROUP BY m.industry;'''
        return run_data(sql, fetch=2)

    def match_info_num(self):
        sql = '''SELECT subquery.pl_status, COUNT(subquery.student_id) AS count
                FROM (
                    SELECT s.student_id, IFNULL(pl.pl_status, 'No_placement') AS pl_status
                    FROM student AS s
                    JOIN student_skills AS ss ON s.student_id = ss.student_id
                    JOIN skills AS sk ON ss.skill_id = sk.skill_id
                    LEFT JOIN placement AS pl ON ss.student_id = pl.student_id
                    GROUP BY s.student_id, pl.pl_status
                ) AS subquery
                GROUP BY subquery.pl_status;'''
        return run_data(sql, fetch=2)


class AddMentor:
    def check_user_name(self, data):
        sql = '''SELECT user_name FROM user WHERE user_name = %s'''
        para = (data['user_name'],)
        return run_data(sql, para, fetch=1)

    def generate_username(self, data):
        sql = '''SELECT user_name FROM user WHERE user_name = %s'''
        para = (data['user_name'],)
        result = run_data(sql, para, fetch=1)
        num = 1
        while result:
            data['user_name'] = data['user_name'] + str(num)
            num += 1
            return self.generate_username(data)
        # print(data['user_name'])
        return data['user_name']

    def add_user(self, data):
        sql = '''INSERT INTO user (user_name, password, role) VALUES (%s, %s, %s)'''
        para = (data['user_name'], data['password'], 'mentor')
        run_data(sql, para)

    def add_mentor(self, data):
        sql = '''INSERT INTO mentor (user_name, first_name, last_name, company_name, email, phone, industry, location) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        para = (data['user_name'], data['first_name'], data['last_name'], data['company_name'],
                data['email'], data['phone'], data['industry'], data['location'])
        run_data(sql, para)

    def add_project(self, data):
        sql = '''INSERT INTO project (mentor_id, project_title, project_summary, place_num, start_date) VALUES (%s, %s, %s, %s, %s)'''
        para = (data['mentor_id'], data['project_title'],
                data['project_summary'], data['place_num'], data['start_date'])
        run_data(sql, para)

    def add_skills_required(self, data):
        for skill_id in data['skills']:
            sql = '''INSERT INTO project_requirement (project_id, skill_id) VALUES (%s, %s)'''
            para = (data['project_id'], skill_id)
            run_data(sql, para)

    def add_placement(self, data):
        sql = '''INSERT INTO placement (student_id, project_id, pl_status) VALUES (%s, %s, %s)'''
        para = (data['student_id'], data['project_id'], 'confirmed')
        run_data(sql, para)


class VerificationMethod:
    def __init__(self, user_name, email=None):
        self.user_name = user_name
        self.email = email

    def verify_email_student(self, user_name, email):
        sql = f"select email from student where email='{email}' and user_name != '{user_name}';"
        return run_data(sql, fetch=1)


class StudentMatch:
    def __init__(self, student_id=None, project_id=None):
        self.student_id = student_id
        self.project_id = project_id

    def searchstudent_skills(self):
        sql = '''select s.student_id, ss.skill_id
        from student as s
        join student_skills as ss on s.student_id = ss.student_id
        where s.student_id = %s
        '''
        para = (self.student_id,)
        return run_data(sql, para, fetch=2)

    def searchcompany_skills(self):
        sql2 = '''select project_id, skill_id from project_requirement;'''
        return run_data(sql2, fetch=2)

    def available_slots(self):
        sql = '''SELECT p.project_id, p.place_num - COUNT(pl.project_id) AS Available_count
                FROM project as p
                LEFT JOIN placement as pl ON p.project_id = pl.project_id AND pl.pl_status = 'Confirmed'
                GROUP BY p.project_id
                HAVING Available_count > 0;'''
        return run_data(sql, fetch=2)

    def project_info(self):
        sql = '''SELECT p.project_id, p.mentor_id, p.project_title, p.project_summary, 
                m.industry, m.location, m.company_name
                FROM project as p
                join mentor as m on p.mentor_id = m.mentor_id'''
        return run_data(sql, fetch=2)

    def update_match_project(self):
        sql = '''INSERT INTO placement (student_id,project_id,pl_status) VALUES (%s,%s,"Confirmed");'''
        para = (self.student_id, self.project_id)
        run_data(sql, para)

    def company_filter(self):
        sql = '''SELECT m.mentor_id, m.company_name, m.industry, m.location, 
            p.project_id, p.project_title, p.project_summary, p.place_num, (SELECT COUNT(*) FROM placement 
            WHERE project_id = p.project_id AND pl_status = 'matched') AS "students_matched", 
            ( SELECT COUNT(*) FROM placement WHERE project_id = p.project_id AND pl_status = 'confirmed') AS 'confirmed',
            p.start_date FROM mentor AS m JOIN project AS p ON m.mentor_id = p.mentor_id
            LEFT JOIN placement AS pl ON p.project_id = pl.project_id
            GROUP BY m.mentor_id, p.project_id
            HAVING (p.place_num-confirmed)>0;'''
        return run_data(sql, fetch=2)

    def company_full(self):
        sql = '''SELECT m.mentor_id, m.company_name, m.industry, m.location, 
            p.project_id, p.project_title, p.project_summary, p.place_num, (SELECT COUNT(*) FROM placement 
            WHERE project_id = p.project_id AND pl_status = 'matched') AS "students_matched", 
            ( SELECT COUNT(*) FROM placement WHERE project_id = p.project_id AND pl_status = 'confirmed') AS 'confirmed',
            p.start_date FROM mentor AS m JOIN project AS p ON m.mentor_id = p.mentor_id
            LEFT JOIN placement AS pl ON p.project_id = pl.project_id
            GROUP BY m.mentor_id, p.project_id
            HAVING (p.place_num-confirmed)=0;'''
        return run_data(sql, fetch=2)


class Notification:
    def __init__(self, user_name=None, data=None, send_to=None, current_time=None, name=None):
        self.user_name = user_name
        self.data = data
        self.current_time = current_time
        self.name = name
        self.send_to = send_to

    def sentMail(self, user_name, data, send_to, current_time):
        sql = '''insert into notification (subjects, Send_from, Send_to, message, receive_date, status) 
                    values (%s,%s,%s,%s,%s,%s); '''
        para = (data['subject'], user_name, send_to,
                data['message'], current_time, 'unread')
        run_data(sql, para)

    def searchName(self):
        sql = """SELECT u.user_name, CONCAT(COALESCE(s.first_name, m.first_name, st.first_name), ' ', 
                        COALESCE(s.last_name, m.last_name, st.last_name)) AS name
                FROM user AS u
                LEFT JOIN staff AS s ON u.user_name = s.user_name
                LEFT JOIN mentor AS m ON u.user_name = m.user_name
                LEFT JOIN student AS st ON u.user_name = st.user_name;
            """

        return run_data(sql,fetch=2)
    
    def findName(self,user_name):
        sql="""SELECT u.user_name, CONCAT(COALESCE(s.first_name, m.first_name, st.first_name), ' ', 
                        COALESCE(s.last_name, m.last_name, st.last_name)) AS name
                FROM user AS u
                LEFT JOIN staff AS s ON u.user_name = s.user_name
                LEFT JOIN mentor AS m ON u.user_name = m.user_name
                LEFT JOIN student AS st ON u.user_name = st.user_name
                where u.user_name = %s;"""
        para = (user_name,)
        return run_data(sql,para,fetch=1)


    def searchUsername(self, name):
        sql = """SELECT u.user_name, CONCAT(COALESCE(s.first_name, m.first_name, st.first_name), ' ', 
                COALESCE(s.last_name, m.last_name, st.last_name)) AS name
                FROM user AS u
                LEFT JOIN staff AS s ON u.user_name = s.user_name
                LEFT JOIN mentor AS m ON u.user_name = m.user_name
                LEFT JOIN student AS st ON u.user_name = st.user_name
                WHERE CONCAT(COALESCE(s.first_name, m.first_name, st.first_name), ' ', 
                COALESCE(s.last_name, m.last_name, st.last_name)) = %s;"""
        para = (name,)
        return run_data(sql, para, fetch=1)
