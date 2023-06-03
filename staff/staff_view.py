from flask import (Blueprint, render_template, request, Flask, send_file,
                   redirect, views, g, flash, session, current_app, url_for, jsonify)
from models import *
from functools import wraps
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


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
        user_name = session.get('user_name')
        if user_name:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner


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


@staff_bp.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole, "staff_info": g.staff_info}


class StaffDashboard(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        staff_info = Staff(g.user_name).get_staff()
        session['staff_info'] = staff_info
        content = {
            "title": 'Staff Dashboard',
            "staff_info": staff_info
        }
        return render_template('staff/staff.html', **content)


staff_bp.add_url_rule(
    '/', view_func=StaffDashboard.as_view('staff'))


class StaffProfile(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
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
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self, data=None):
        # for the number card display
        match_info_num = Staff().match_info_num()
        match_info = {}
        for info_num in match_info_num:
            pl_status = info_num['pl_status']
            count = info_num['count']
            match_info[pl_status] = count

        # for search function
        option = request.args.get('option')
        if data:
            student_list = Staff(data=data).search_student_list(data=data)
            record = len(student_list)
        else:
            student_list = Staff(g.user_name).get_student_list()
            record = 0

        if option and option != 'all':
            student_list = Staff(g.user_name, option=option).student_class()

        if student_list:
            # status_options = [('Matched'), ('Interviewed'), ('Not Interested'),
            #                   ('Confirmed'), ('Cancelled'), ('Intervention Needed')]
            full_list = []
            for list in student_list:
                full_list.append(list)
            student_list, pagination = paginate_func(full_list, per_page=9)
            context = {
                "pagination": pagination,
                "student_list": student_list,
                # "status_options": status_options,
                "match_info": match_info
            }
            # define number of records found
            if record != 0:
                context["record"] = record
            return render_template('/staff/student_list.html', **context)
        else:
            flash('No result found', 'red')
            return self.get(data=None)

    def post(self):
        search = request.args.get('search')
        # filter function
        if search:
            search_result = request.form.to_dict()
            return self.get(data=search_result)

        else:
            data = request.form.to_dict()
            print(data)
            return self.get()


staff_bp.add_url_rule(
    '/student_list', view_func=ViewStudentList.as_view('staff_student_list'))


class StudentsNeedProject(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        student_need = Staff(g.user_name).get_student_need()
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
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        student_matched_list = Staff(g.user_name).get_student_matched()
        full_list = []
        for item in student_matched_list:
            full_list.append(item)
        student_matched_list, pagination = paginate_func(full_list, per_page=8)
        context = {
            "title": 'Students Matched',
            "pagination": pagination,
            "student_matched_list": student_matched_list,
        }
        return render_template('staff/student_list.html', **context)


staff_bp.add_url_rule(
    '/students_matched', view_func=StudentsMatched.as_view('staff_students_matched'))


class StaffProjects(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self, data=None):

        option = request.args.get('option')
        if option == 'Available':
            project_list = StudentMatch().company_filter()
            record = len(project_list)
            # flash(f'{record} records found for available projects')
        elif option == 'Full':
            project_list = StudentMatch().company_full()
            if not project_list:
                record = '0'
                project_list = Staff(g.user_name).get_project_list()
                flash('No Completed Projects', 'red')
            else:
                record = len(project_list)
        else:
            project_list = Staff(g.user_name).get_project_list()
            record = len(project_list)

        if data:
            project_list = Staff(
                g.user_name, data=data).search_project_list(data=data)
            record = len(project_list)

        if project_list:
            full_list = []
            for item in project_list:
                full_list.append(item)
            # print(full_list)
            project_list, pagination = paginate_func(full_list, per_page=6)
            context = {
                "title": 'Companies and Projects',
                "pagination": pagination,
                "project_list": project_list,
            }
            if record != 0:
                context['record'] = record
            return render_template('staff/projects_mentors.html', projects=project_list, **context)
        else:
            flash('No result found', 'red')
            return self.get(data=None)

    def post(self):
        data = request.form.to_dict()
        return self.get(data=data)


staff_bp.add_url_rule(
    '/projects', view_func=StaffProjects.as_view('comp_projects'))


class StaffMentors(views.MethodView):
    decorators = [login_required]
 # decorators = [catch_exception]

    def get(self, data=None):
        if data:
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
            print(mentor_list)
            context = {
                "pagination": pagination,
                "mentor_list": mentor_list,
            }
            if record != 0:
                context['record'] = record
            return render_template('staff/projects_mentors.html', title='All Mentors',  **context)
        else:
            flash('No result found', 'red')
            return self.get()

    def post(self):
        data = request.form.to_dict()
        return self.get(data=data)


staff_bp.add_url_rule(
    '/mentors', view_func=StaffMentors.as_view('all_mentors'))


class StaffMatch(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        project_id = request.args.get('project_id')
        location = request.args.get('location')
        available_slots = Projects().available_slots(
            project_id)['available_slots']
        confirmed_num = Projects().confirm_count(project_id)
        skills_required = Projects().skills_required(project_id)
        student_list = Projects().match_students(project_id)
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
        student_id = request.form.get('student_id')
        project_id = request.form.get('project_id')

        sql = f'''select * from placement where student_id = {student_id} and project_id = {project_id} and pl_status = "Matched";'''
        result = run_data(sql, fetch=2)

        data = {
            'student_id': student_id,
            'project_id': project_id,
            'status': 'Confirmed'
        }

        try:
            reference = request.referrer
            reference = reference.split('http://127.0.0.1:5000')[1]
            if result:
                Mentor(user_name=g.user_name,
                       data=data).update_placement_status(data=data)
            else:
                Mentor(user_name=g.user_name,
                       data=data).new_placement(data=data)
            flash(
                f"Student {data['student_id']} has been matched to project {data['project_id']}")
            return redirect(f'{reference}')
        except Exception as e:
            flash(f'Failed to add student to project! {e}', 'red')
            return self.get()


staff_bp.add_url_rule(
    '/match', view_func=StaffMatch.as_view('match_students_project'))


class StaffAddMentor(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        all_skills = Skills().all_skills()
        content = {
            "title": 'Add Mentor',
            "all_skills": all_skills,
            "add_mentor": True
        }
        return render_template('staff/add_mentor_project.html', **content)

    def post(self):
        data = request.form.to_dict()
        data['skills'] = request.form.getlist('skills')
        data['password'] = hashlib.sha256(
            data['password'].encode('utf-8')).hexdigest()
        result = AddMentor().check_user_name(data)
        print(result)
        if result:
            flash(
                f"Username {data['user_name']} already exists. Please try again.", 'red')
            return redirect(url_for('staff.staff_add_mentor'))
        else:
            AddMentor().add_user(data)
            AddMentor().add_mentor(data)

            flash(
                f"{data['first_name']}\'s information added successfully!")
            return redirect(url_for('staff.all_mentors'))


staff_bp.add_url_rule(
    '/add_mentor', view_func=StaffAddMentor.as_view('staff_add_mentor'))


class StaffPlacementInfo(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        report = Staff().palcement_report()
        category = Staff().industry_category()
        print(report)
        print(category)
        # {'students_needing_project_in_semester_2': 35, 'total_students': 42, 'available_placements': 162, 'potential_placements': 2,
        # 'student_matched': 3, 'student_confirmed': 2, 'total_projects': 25, 'total_mentors': 24, 'total_companies': 24}

        # [{'Projects': 1, 'industry': 'Cybersecurity', 'Placement Available': Decimal('1')},
        #  {'Projects': 3, 'industry': 'Website Development', 'Placement Available': Decimal('4')},
        # {'Projects': 3, 'industry': 'IT Consulting', 'Placement Available': Decimal('5')},
        # {'Projects': 5, 'industry': 'Software Development', 'Placement Available': Decimal('12')},
        # {'Projects': 1, 'industry': 'Web Development', 'Placement Available': Decimal('1')},

        # Create the bar chart for student counts
        bar_fig = go.Figure(data=[
            go.Bar(x=['Total Students'], y=[report['total_students']],
                   name='Total Students', marker_color='blue'),
            go.Bar(x=['Students Needing Project'], y=[report['students_needing_project_in_semester_2']],
                   name='Students Needing Project', marker_color='orange'),
            go.Bar(x=['Student Matched'], y=[report['student_matched']],
                   name='Student Matched', marker_color='green'),
            go.Bar(x=['Student Confirmed'], y=[report['student_confirmed']],
                   name='Student Confirmed', marker_color='purple')
        ])

        # Set the layout for the bar chart
        bar_fig.update_layout(title='Student Placement Status',
                              xaxis_title='Categories',
                              yaxis_title='Count',
                              barmode='group')

        # Extract industry categories and placement availability
        industry_categories = [item['industry'] for item in category]
        placement_counts = [item['Placement Available'] for item in category]

        # Create the bar chart for placement availability
        bar_2_fig = go.Figure(data=[
            go.Bar(x=industry_categories,
                   y=placement_counts, marker_color=['#1f77b4', '#ff7f0e', '#2ca02c',  '#9467bd', '#8c564b',
                                                     '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1f77b4', '#ff7f0e',
                                                     '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',])
        ])

        # Set the layout for the bar chart
        bar_2_fig.update_layout(
            title='Placement Availability by Industry Category',
            xaxis_title='Industry Category',
            yaxis_title='Number of Available Placements'
        )

        # Extract project names and their availability
        project_industry = [item['industry'] for item in category]
        project_availability = [item['Placement Available']
                                for item in category]

        # Create the donut chart for project distribution and availability
        donut_fig = go.Figure(data=[
            go.Pie(
                labels=project_industry,
                values=project_availability,
                hole=0.4,
                marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c',
                               '#d62728', '#9467bd'],  # Custom colors
                name="Available Projects",
                domain={"x": [0, 0.45]},
            ),
        ])

        # Set the layout for the donut chart
        donut_fig.update_layout(
            title='Project Distribution and Availability',
            annotations=[
                dict(text='Available Projects', x=0.2,
                     y=0.5, font_size=20, showarrow=False)
            ],
            showlegend=False
        )

        # Convert the plot to HTML

        bar_html = bar_fig.to_html(full_html=False)
        bar_2_html = bar_2_fig.to_html(full_html=False)
        donut_html = donut_fig.to_html(full_html=False)

        return render_template('staff/placement_report.html',
                               title='Placement Info',
                               placement_report=report,
                               bar_chart=bar_html,
                               bar_2_chart=bar_2_html,
                               donut_chart=donut_html)


staff_bp.add_url_rule(
    '/placement_info', view_func=StaffPlacementInfo.as_view('staff_placement_info'))


class SearchCompanies(views.MethodView):
    decorators = [login_required]

    def get(self):
        companies = run_data(
            'select distinct company_name from mentor;', fetch=2)
        companies = [item['company_name'] for item in companies]
        # print(companies)

        search_text = request.args.get('search', '')
        # print(search_text)
        matching_companies = [company for company in companies if company.lower(
        ).startswith(search_text.lower())]
        if not matching_companies:
            matching_companies = ['No Match results']
        print(matching_companies)

        return jsonify({'companies': matching_companies})


staff_bp.add_url_rule(
    '/search_company', view_func=SearchCompanies.as_view('search_company'))


class StaffMatchStudent(views.MethodView):
    decorators = [login_required]

    def get(self):
        student_id = request.args.get('student_id')
        sql = f'''select location from student where student_id = {student_id};'''
        location = run_data(sql, fetch=1)

        student_name = request.args.get('student_name')

        student_skills_list = StudentMatch(student_id).searchstudent_skills()
        student_skills_set = set([item['skill_id']
                                 for item in student_skills_list])

        company_skill_list = StudentMatch().searchcompany_skills()
        company_skills = {}

        for item in company_skill_list:
            project_id = item['project_id']
            skill_id = item['skill_id']
            if project_id not in company_skills:
                company_skills[project_id] = set()
            company_skills[project_id].add(skill_id)

        skill_match_count = {}

        for project_id, skill_set in company_skills.items():
            matched_number = len(skill_set & student_skills_set)
            skill_match_count[project_id] = {'matched_skills': matched_number}

        skill_match_count = sorted(skill_match_count.items(
        ), key=lambda x: x[1]['matched_skills'], reverse=True)
        skill_match_count = dict(skill_match_count)

        # display only 9 top options for staff to choose
        skill_match_count = dict(list(skill_match_count.items())[:10])

        available_slot = StudentMatch().available_slots()

        project_details_list = StudentMatch().project_info()

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
        student_id = request.form.get('student_id')
        project_id = request.form.get('project_id')
        StudentMatch(student_id, project_id).update_match_project()

        flash(
            f'student_id: {student_id} has been assigned to project_id: {project_id}')

        return redirect(url_for('staff.staff_student_list'))


staff_bp.add_url_rule(
    '/staff_match_student', view_func=StaffMatchStudent.as_view('staff_match_student'))
