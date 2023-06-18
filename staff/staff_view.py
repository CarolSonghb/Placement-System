from flask import (Blueprint, render_template, request, Flask, send_file,
                   redirect, views, g, flash, session, current_app, url_for, jsonify)
from models import *
from functools import wraps
from pyecharts.charts import Bar, Liquid, Line, Pie
from pyecharts import options as opts
from pyecharts.globals import SymbolType

# build blueprint for staff user
staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

# add error handler to catch exception


@staff_bp.errorhandler(500)
def catch_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return render_template('500.html', error=e), 500
    return decorated_function


# decorators to verify login status
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # get user_name from session
        user_name = session.get('user_name')
        if user_name:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner

# add global variable to store user_name, userrole and staff_info


@staff_bp.before_request
def my_before_request():
    user_name = session.get('user_name')
    userrole = session.get('userrole')
    staff_info = session.get('staff_info')

    if user_name:
        setattr(g, 'user_name', user_name)
        setattr(g, 'userrole', userrole)
        setattr(g, 'staff_info', staff_info)
    else:
        setattr(g, 'user_name', None)
        setattr(g, 'userrole', None)
        setattr(g, 'staff_info', None)

# context processor to pass global variable to html


@staff_bp.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole, "staff_info": g.staff_info}


class StaffDashboard(views.MethodView):
    # add login_required decorator to verify login status and catch_exception decorator to catch exception
    decorators = [login_required, catch_exception]

    def get(self):
        # get staff information from database
        staff_info = Staff(g.user_name).get_staff()
        session['staff_info'] = staff_info
        # set title and pass staff_info to html
        content = {
            "title": 'Staff Dashboard',
            "staff_info": staff_info
        }
        return render_template('staff/staff.html', **content)


# build route for staff dashboard
staff_bp.add_url_rule(
    '/', view_func=StaffDashboard.as_view('staff'))


class StaffProfile(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get staff information from database, pass information to html
        staff_info = Staff(g.user_name).get_staff()
        content = {
            "title": 'Staff Profile',
            "staff_info": staff_info
        }
        return render_template('staff/staff_profile.html', **content)

    def post(self):
        data = request.form.to_dict()
        Staff(g.user_name).update_staff(data)
        flash(
            f"{data['first_name']}\'s information updated successfully!")
        return redirect(url_for('staff.staff_profile'))


staff_bp.add_url_rule(
    '/profile', view_func=StaffProfile.as_view('staff_profile'))


# add show student whole list function for staff user, add pagination function to models.py
class ViewStudentList(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self, data=None):
        # get match information from database
        match_info_num = Staff().match_info_num()
        match_info = {}
        # convert match information to dictionary
        for info_num in match_info_num:
            pl_status = info_num['pl_status']
            count = info_num['count']
            match_info[pl_status] = count

        # get search data from request
        option = request.args.get('option')
        if data:
            # get student list from database
            student_list = Staff(data=data).search_student_list(data=data)
            record = len(student_list)
        else:
            # get student list from database
            student_list = Staff(g.user_name).get_student_list()
            record = 0

        if option and option != 'all':
            # get student list from database
            student_list = Staff(g.user_name, option=option).student_class()

        if student_list:
            # convert student list to a list
            full_list = []
            for list in student_list:
                full_list.append(list)
                # define pagination function
            student_list, pagination = paginate_func(full_list, per_page=9)
            context = {
                "pagination": pagination,
                "student_list": student_list,
                "match_info": match_info
            }
            # if search result is not empty, pass record to html
            if record != 0:
                context["record"] = record
            return render_template('/staff/student_list.html', **context)
        else:
            flash('No result found', 'red')
            return self.get(data=None)

    def post(self):
        search = request.args.get('search')
        # filter function for search student list
        if search:
            search_result = request.form.to_dict()
            return self.get(data=search_result)

        else:
            # convert form data to dictionary
            data = request.form.to_dict()

            return self.get()


# define route for student list
staff_bp.add_url_rule(
    '/student_list', view_func=ViewStudentList.as_view('staff_student_list'))


class StudentsNeedProject(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get student need project information from database
        student_need = Staff(g.user_name).get_student_need()
        # define status options
        status_options = [('Matched'), ('Interviewed'), ('Not Interested'),
                          ('Confirmed'), ('Cancelled'), ('Intervention Needed')]
        full_list = []
        for item in student_need:
            full_list.append(item)
        student_need, pagination = paginate_func(full_list, per_page=8)
        context = {
            "title": 'Students Need Project',
            "pagination": pagination,
            "student_need_list": student_need,
            "status_options": status_options,
        }
        return render_template('staff/student_list.html', **context)

    def post(self):

        data = request.form.to_dict()
        print(data)
        return self.get()


staff_bp.add_url_rule(
    '/students_need_project', view_func=StudentsNeedProject.as_view('staff_students_need'))


class StudentsMatched(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get student matched list information from database
        student_matched_list = Staff(g.user_name).get_student_matched()
        full_list = []
        for item in student_matched_list:
            full_list.append(item)
        student_matched_list, pagination = paginate_func(full_list, per_page=8)
        # pack context data as a dictionary and send to html
        context = {
            "title": 'Students Matched',
            "pagination": pagination,
            "student_matched_list": student_matched_list,
        }
        return render_template('staff/student_list.html', **context)


# add url rule for student matched list
staff_bp.add_url_rule(
    '/students_matched', view_func=StudentsMatched.as_view('staff_students_matched'))


class StaffProjects(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self, data=None):
        #  get query option from dropdown list
        option = request.args.get('option')
        if option == 'Available':
            # get the project list which are still available  from database
            project_list = StudentMatch().company_filter()
            # get the number of projects
            record = len(project_list)
        elif option == 'Full':
            # get the project list which placement is full from database
            project_list = StudentMatch().company_full()
            if not project_list:
                # if no project, set record to 0
                record = '0'
                project_list = Staff(g.user_name).get_project_list()
                flash('No Completed Projects', 'red')
            else:
                record = len(project_list)
        else:
            project_list = Staff(g.user_name).get_project_list()
            record = len(project_list)
        # if search bar is data, get the project list from database
        if data:
            project_list = Staff(
                g.user_name, data=data).search_project_list(data=data)
            record = len(project_list)
            # if returned a result, send the result to html
        if project_list:
            full_list = []
            # convert project list to a list
            for item in project_list:
                full_list.append(item)
                # define pagination function
            project_list, pagination = paginate_func(full_list, per_page=6)
            # pack context data as a dictionary and send to html
            context = {
                "title": 'Companies and Projects',
                "pagination": pagination,
                "project_list": project_list,
            }
            # if search result is not empty, pass record to html
            if record != 0:
                context['record'] = record
            return render_template('staff/projects_mentors.html', projects=project_list, **context)
        else:
            flash('No result found', 'red')
            return self.get(data=None)

    def post(self):
        data = request.form.to_dict()
        return self.get(data=data)


# add url rule for companies and project list
staff_bp.add_url_rule(
    '/projects', view_func=StaffProjects.as_view('comp_projects'))

# class view for staff view mentor list


class StaffMentors(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self, data=None):

        if data:
            # get mentor list from database
            mentor_list = Staff(
                g.user_name, data=data).search_mentor_list(data=data)
            record = len(mentor_list)
        else:
            mentor_list = Staff(g.user_name).get_mentor_list()
            record = 0

        if mentor_list:
            full_list = []
            for item in mentor_list:
                full_list.append(item)
            mentor_list, pagination = paginate_func(full_list, per_page=8)
            # pack mentors' data as a dictionary and send to html
            context = {
                "pagination": pagination,
                "mentor_list": mentor_list,
            }
            # if search result is not empty, pass record to html
            if record != 0:
                context['record'] = record
            return render_template('staff/projects_mentors.html', title='All Mentors',  **context)
        else:
            flash('No result found', 'red')
            return self.get()

    def post(self):
        data = request.form.to_dict()
        return self.get(data=data)


# add url rule for mentor list
staff_bp.add_url_rule(
    '/mentors', view_func=StaffMentors.as_view('all_mentors'))


class StaffMatch(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get project id from url
        project_id = request.args.get('project_id')
        location = request.args.get('location')
        # get available slots from database
        available_slots = Projects().available_slots(
            project_id)['available_slots']
        # get confirmed number from database
        confirmed_num = Projects().confirm_count(project_id)
        # get skills required by the projects from database
        skills_required = Projects().skills_required(project_id)
        # get student list from database
        student_list = Projects().match_students(project_id)
        # pack context data as a dictionary and send to html
        context = {
            "title": 'Match Students and Projects',
            "skills_required": skills_required,
            "project_id": project_id,
            "student_list": student_list,
            "available_slots": available_slots,
            "location": location,
            "confirmed_num": confirmed_num
        }
        return render_template('staff/matching.html', **context)

    def post(self):
        # get project id from url
        student_id = request.form.get('student_id')
        # get project id from url
        project_id = request.form.get('project_id')
        # get mtached stduents information from database
        sql = f'''select * from placement where student_id = {student_id} and project_id = {project_id} and pl_status = "Matched";'''
        result = run_data(sql, fetch=2)
        # pack data as a dictionary
        data = {
            'student_id': student_id,
            'project_id': project_id,
            'status': 'Confirmed'
        }

        try:
            # get the previous url
            reference = request.referrer
            # remove the host name from the url
            reference = reference.split('http://127.0.0.1:5000')[1]
            if result:
                # if the student has been matched to the project, update the placement status
                Mentor(user_name=g.user_name,
                       data=data).update_placement_status(data=data)
            else:
                # if the student has not been matched to the project, add the student to the project
                Mentor(user_name=g.user_name,
                       data=data).new_placement(data=data)
            flash(
                f"Student {data['student_id']} has been matched to project {data['project_id']}")
            return redirect(f'{reference}')
        except Exception as e:
            flash(f'Failed to add student to project! {e}', 'red')
            return self.get()


# add url rule for matching students and projects
staff_bp.add_url_rule(
    '/match', view_func=StaffMatch.as_view('match_students_project'))

# staff view for adding new mentor


class StaffAddMentor(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get all skills listfrom database
        all_skills = Skills().all_skills()
        # pack data as a dictionary and send to html
        content = {
            "title": 'Add Mentor',
            "all_skills": all_skills,
            "add_mentor": True
        }
        return render_template('staff/add_mentor_project.html', **content)

    def post(self):
        # convert form data to dictionary
        data = request.form.to_dict()
        # get required skills from form
        data['skills'] = request.form.getlist('skills')
        # set default password
        data['password'] = '1111'
        # check if the username already exists
        result = AddMentor().check_user_name(data)
        if result:
            flash(
                f"Username {data['user_name']} already exists. Please try again.", 'red')
            return redirect(url_for('staff.staff_add_mentor'))
        else:
            # add new user and mentor to database
            AddMentor().add_user(data)
            AddMentor().add_mentor(data)

            flash(
                f"{data['first_name']}\'s information added successfully!")
            return redirect(url_for('staff.all_mentors'))


# add url rule for adding new mentor
staff_bp.add_url_rule(
    '/add_mentor', view_func=StaffAddMentor.as_view('staff_add_mentor'))


class StaffPlacementInfo(views.MethodView):
    decorators = [login_required]

    def get(self):
        # get total students number from database
        total_students = run_data(
            'select count(*) as total_student from student;', fetch=1)['total_student']
        # get total students number who are needing projects from database
        students_needing_project_in_semester_2 = run_data(
            'select count(student_id) as student_2 from student where semester_to_place = 2;', fetch=1)['student_2']
        # get total projects number from database
        total_projects = run_data(
            'select count(*) as total_projects from project;', fetch=1)['total_projects']
        # get total mentors number from database
        total_mentors = run_data(
            'select count(*) as total_mentors from mentor;', fetch=1)['total_mentors']
        total_companies = total_mentors
        # get studnet matched number from database
        student_matched = run_data(
            'select count(student_id) as student_matched from placement where pl_status = "Matched";', fetch=1)['student_matched']
        # get student confirmed number from database
        student_confirmed = run_data(
            'select count(student_id) as student_confirmed from placement where pl_status = "Confirmed";', fetch=1)['student_confirmed']
        # get total available placements from database
        total_placements = run_data(
            'SELECT SUM(place_num) AS total_place_num FROM project;', fetch=1)['total_place_num']
        # get the student percentage who are needing projects
        student_percentage = int(student_confirmed) / int(total_students)

        # data for location distribution diagram
        student_location_list = run_data(
            'SELECT location, COUNT(*) AS student_count FROM student GROUP BY location;', fetch=2)
        # get student number from database
        student_counts = [item['student_count']
                          for item in student_location_list]
        # get student location from database
        location_counts = [item['location'] for item in student_location_list]
        # create bar chart
        bar1 = (
            Bar()
            .add_xaxis(location_counts)
            .add_yaxis('student_number', student_counts,
                       itemstyle_opts=opts.ItemStyleOpts(color='#336699'))
        )
        # data for company distribution diagram
        company_location_list = run_data(
            'SELECT location, COUNT(*) AS company_count FROM mentor GROUP BY location;', fetch=2)
        # get company number from database
        company_counts = [item['company_count']
                          for item in company_location_list]
        # get company locations from database
        location_company = [item['location'] for item in company_location_list]
        # create bar chart
        bar2 = (
            Bar()
            .add_xaxis(location_company)
            .add_yaxis('company_number', company_counts,
                       itemstyle_opts=opts.ItemStyleOpts(color='#336699'))
        )

# create liquid pic
        liquid = (
            Liquid()
            .add("lq", [student_percentage])
            .set_global_opts(title_opts=opts.TitleOpts(pos_left='center', title="Student Confirmed Rate"))
        )

# data for Line chart
        industry = run_data(
            'SELECT industry, COUNT(*) AS company_count FROM mentor GROUP BY industry;', fetch=2)
        # get industry name from database
        industry_name = [item['industry'] for item in industry]
        # get company number from database
        company_counts = [item['company_count'] for item in industry]
# create line chart
        line1 = (
            Line()
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    pos_left='center', title="Company Distribution By Different Industries"),
                tooltip_opts=opts.TooltipOpts(is_show=False),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
            )
            .add_xaxis(xaxis_data=industry_name)
            .add_yaxis(
                series_name="",
                y_axis=company_counts,
                symbol="emptyCircle",
                is_symbol_show=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(color='#336699')
            )
        )

# below is for pie chart
        place_num_sql = '''select m.industry, sum(p.place_num) as total_placement_num
                        from project as p
                        join mentor as m
                        on p.mentor_id=m.mentor_id
                        group by m.industry;'''
        industry_info = run_data(place_num_sql, fetch=2)
        industry_list = [item['industry'] for item in industry_info]
        total_placement_num = [item['total_placement_num']
                               for item in industry_info]

        data_pair = [list(z) for z in zip(industry_list, total_placement_num)]
        data_pair.sort(key=lambda x: x[1])

        pie = (
            Pie(init_opts=opts.InitOpts(bg_color="#fff"))
            .add(
                series_name="industry_class",
                data_pair=data_pair,
                rosetype="radius",
                radius="55%",
                center=["70%", "50%"],
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Total Placement Number By Industries",
                    pos_left="40%",
                    pos_top="0",
                    title_textstyle_opts=opts.TextStyleOpts(color="#2c343c"),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
            )
            .set_series_opts(
                tooltip_opts=opts.TooltipOpts(
                    trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"
                ),
                label_opts=opts.LabelOpts(color="#2c343c"),
            )
        )
# pack all the data into content
        content = {
            'total_students': total_students,
            'students_needing_project': students_needing_project_in_semester_2,
            'total_projects': total_projects,
            'total_mentors': total_mentors,
            'total_companies': total_companies,
            'student_matched': student_matched,
            'student_confirmed': student_confirmed,
            'total_placements': total_placements
        }

        return render_template('staff/placement_report.html', **content,
                               bar_options1=bar1.dump_options(),
                               bar_options2=bar2.dump_options(),
                               liquid_option=liquid.dump_options(),
                               line_options=line1.dump_options(),
                               pie_options=pie.dump_options()
                               )


staff_bp.add_url_rule(
    '/placement_info', view_func=StaffPlacementInfo.as_view('staff_placement_info'))


class SearchCompanies(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get all companies from database
        companies = run_data(
            'select distinct company_name from mentor;', fetch=2)
        # convert company name into a list
        companies = [item['company_name'] for item in companies]

        # get search text from request
        search_text = request.args.get('search', '')
        # filter companies by search text
        matching_companies = [company for company in companies if company.lower(
        ).startswith(search_text.lower())]
        if not matching_companies:
            matching_companies = ['No Match results']
        print(matching_companies)

        return jsonify({'companies': matching_companies})


# a
staff_bp.add_url_rule(
    '/search_company', view_func=SearchCompanies.as_view('search_company'))


class StaffMatchStudent(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get student id from request
        student_id = request.args.get('student_id')
        # query student location from database
        sql = f'''select location from student where student_id = {student_id};'''
        location = run_data(sql, fetch=1)
        # get student name from url
        student_name = request.args.get('student_name')
        # query student skills from database
        student_skills_list = StudentMatch(student_id).searchstudent_skills()
        # convert student skills into a set
        student_skills_set = set([item['skill_id']
                                 for item in student_skills_list])
        # query company required skills from database
        company_skill_list = StudentMatch().searchcompany_skills()
        company_skills = {}
        # convert company skills into a dictionary
        for item in company_skill_list:
            project_id = item['project_id']
            skill_id = item['skill_id']
            if project_id not in company_skills:
                company_skills[project_id] = set()
            company_skills[project_id].add(skill_id)
        # set up a dictionary to store matched skills
        skill_match_count = {}
        # calculate matched skills
        for project_id, skill_set in company_skills.items():
            matched_number = len(skill_set & student_skills_set)
            skill_match_count[project_id] = {'matched_skills': matched_number}
        # sort matched skills in descending order
        skill_match_count = sorted(skill_match_count.items(
        ), key=lambda x: x[1]['matched_skills'], reverse=True)
        skill_match_count = dict(skill_match_count)

        # display only 9 top options for staff to choose
        skill_match_count = dict(list(skill_match_count.items())[:10])
        # query available slots from database
        available_slot = StudentMatch().available_slots()
        # query project details from database
        project_details_list = StudentMatch().project_info()
        # convert project details into a list
        content = {
            "title": "Match Students",
            "student_name": student_name,
            "student_id": student_id,
            "location": location,
            "skill_match_count": skill_match_count,
            "available_slot": available_slot,
            "project_details_list": project_details_list
        }

        return render_template('/staff/matching.html', **content)

    def post(self):
        # get student id and project id from request
        student_id = request.form.get('student_id')
        project_id = request.form.get('project_id')
        # update student match project in database
        StudentMatch(student_id, project_id).update_match_project()

        flash(
            f'student_id: {student_id} has been assigned to project_id: {project_id}')

        return redirect(url_for('staff.staff_student_list'))


# add url rule for staff match student
staff_bp.add_url_rule(
    '/staff_match_student', view_func=StaffMatchStudent.as_view('staff_match_student'))
