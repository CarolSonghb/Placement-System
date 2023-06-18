from flask import (Blueprint, render_template, request,
                   redirect, views, g, flash, session, current_app, url_for, jsonify)
from models import *
from webforms import RegisterForm
from functools import wraps
import os
from flask_mail import Message, Mail
import hashlib
from datetime import datetime


# create a blueprint for mentor
mentor_bp = Blueprint('mentor', __name__, url_prefix='/mentor')

# error handler for 500 in mentor blueprint


@mentor_bp.errorhandler(500)
def catch_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return render_template('500.html', error=e), 500
    return decorated_function


# login required decorator for mentor blueprint


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        user_name = session.get('user_name')
        if user_name:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner

# set global variables for mentor blueprint


@mentor_bp.before_request
def my_before_request():
    user_name = session.get('user_name')
    userrole = session.get('userrole')
    mentor_id = session.get('mentor_id')
    mentor_info = session.get('mentor_info')

    if user_name:
        setattr(g, 'user_name', user_name)
        setattr(g, 'userrole', userrole)
        setattr(g, 'mentor_id', mentor_id)
        setattr(g, 'mentor_info', mentor_info)
    else:
        setattr(g, 'user_name', None)
        setattr(g, 'userrole', None)
        setattr(g, 'mentor_id', None)
        setattr(g, 'mentor_info', None)

# store global variables in context processor


@mentor_bp.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole, "mentor_id": g.mentor_id, "mentor_info": g.mentor_info}

# method view for mentor dashboard


class MentorDashboard(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get mentor info from session
        mentor_info = Mentor(g.user_name).get_mentor()
        # store mentor info in session
        session['mentor_info'] = mentor_info
        # store mentor id in session
        session['mentor_id'] = mentor_info['mentor_id']
        # pass mentor info to template
        content = {
            "title": 'Mentor Dashboard',
            "mentor_info": mentor_info
        }
        return render_template('mentor/mentor.html', **content)


# add url rule for mentor dashboard
mentor_bp.add_url_rule(
    '/', view_func=MentorDashboard.as_view('mentor'))

# method view for mentor profile


class MentorProfile(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # query mentor info from database
        mentor_info = Mentor(g.user_name).get_mentor()
        # store mentor info in session
        session['mentor_info'] = mentor_info
        # store mentor id in session
        session['mentor_id'] = mentor_info['mentor_id']
        # get all locations from database
        locations = Projects(g.user_name).all_locations()
        # store locations in a list
        locations = [location['location'] for location in locations]
        # pass mentor info and locations to template
        content = {
            "title": 'Mentor Profile',
            "locations": locations,
            "mentor_info": mentor_info
        }
        return render_template('mentor/mentor_profile.html', **content)

    def post(self):
        # pack mentor info from form into a dictionary
        mentor_update = request.form.to_dict()
        # update mentor info in database
        Mentor(g.user_name, ).update(mentor_update)
        # flash message once mentor info updated successfully
        flash(
            f"{mentor_update['first_name']}'s information updated successfully!")
        return self.get()


# add url rule for mentor profile
mentor_bp.add_url_rule(
    '/profile', view_func=MentorProfile.as_view('mentor_profile'))


# mentor view/update project info
class MentorProjects(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get all skills from database
        all_skills = Skills().all_skills()
        # get mentor projects from database
        m_projects = Mentor(g.user_name, g.mentor_id).mentor_projects()
        # if no projects, set m_projects to 'No Results'
        if m_projects == []:
            m_projects = 'No Results'
            # pass all skills and m_projects to template
        content = {
            "title": 'Mentor Projects',
            "projects": m_projects,
            "all_skills": all_skills
        }
        return render_template('mentor/mentor_projects.html', **content)

    def post(self):
        # pack project info from form into a dictionary
        data = {
            'project_id': request.form.get('project_id'),
            'project_title': request.form.get('project_title'),
            'project_date': request.form.get('project_date'),
            'place_num': request.form.get('place_num'),
            'skills': request.form.getlist('skills'),
            'project_sum': request.form.get('project_sum')
        }
        try:
            # try to update project info in database
            # remove the skills required for the project
            Projects(data=data).remove_skills(data=data)
            # add the skills required for the project
            AddMentor().add_skills_required(data=data)
            # update project info in database
            Projects(data=data).update_project(data=data)
            # flash message once project info updated successfully
            flash(
                f"Project {data['project_id']} information updated successfully!")
            return self.get()
        except Exception as e:
            # flash message if project info updated failed
            flash(f'Failed to update project information! {e}', 'red')
            return self.get()


# add url rule for mentor projects
mentor_bp.add_url_rule(
    '/projects', view_func=MentorProjects.as_view('projects'))

# mentor view/ add preferred students


class PreferredStudent(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get project id of the current mentor
        project_id = Mentor(g.user_name, g.mentor_id).get_project_id()
        # convert project id to a list
        filter_id = [item['project_id'] for item in project_id]

        students = []
        skill_match = []
        num_matched = []

        for id in project_id:
            # get students interested in the project
            students_for_each = Projects(
                id['project_id']).students_interested(id['project_id'])
            # get skill match number for each student
            skill_match_each = Projects(
                id['project_id']).skill_match_number(id['project_id'])
            # get number of students interested in the project
            students.append(students_for_each)
            # get skill match number for each student
            skill_match.append(skill_match_each)
            # get number of matched students for each project
            num_match_each = Projects(
                id['project_id']).match_count(id['project_id'])
            num_matched.append(num_match_each)

        if students:
            # get pagination function
            students[0], pagination = paginate_func(students[0], per_page=6)
        # if no one select this project, page needs to be designed --- later
        else:
            pagination = None
        # pass students, skill_match, pagination, num_matched and filter_id to template
        content = {
            "students_interested_with_project": students,
            "title": 'Preferred Students',
            "skill_match": skill_match,
            "pagination": pagination,
            "flag": 1,
            "num_matched": num_matched,
            "filter_id": filter_id
        }
        return render_template('mentor/mentor_projects.html', **content)

    def post(self):
        # pack student info from form into a dictionary
        data = request.form.to_dict()
        data['status'] = 'Matched'
        try:
            # try to add student plament information with  project
            Mentor(user_name=g.user_name,
                   ).new_placement(data=data)
            # flash message once student added to project successfully
            flash(
                f"Student {data['student_id']} has been matched to project {data['project_id']}")
            return self.get()
        except Exception as e:
            # flash message if student added to project failed
            flash(f'Failed to add student to project! {e}', 'red')
            return self.get()


# add url rule for mentor preferred students
mentor_bp.add_url_rule(
    '/students_interested', view_func=PreferredStudent.as_view('students_interested'))


class MentorMatchedStudents(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # query out  project id of the current mentor
        project_id = Mentor(g.user_name, g.mentor_id).get_project_id()
        num_matched = []
        for id in project_id:
            # query out  number of matched students for each project
            num_match_each = Projects(
                id['project_id']).match_count(id['project_id'])
            num_matched.append(num_match_each)

        m_students = 'all'
        # get project id from  request
        get_id = request.args.get('get_id')
        # get all project id from request
        get_all = request.args.get('all')

        if get_id:
            # query out matched students for each project
            m_students = Mentor(g.user_name, g.mentor_id,
                                get_id).matched_students_withajax()
            if not m_students:
                # if no matched students, return empty
                m_students = 'Empty'

        if get_all:
            # query out all matched students for each project
            m_students = Mentor(g.user_name, g.mentor_id).matched_students()
        # pass m_students and num_matched to template
        content = {
            "title": 'Matched Students',
            "students_matched": m_students,
            "num_matched": num_matched
        }
        return render_template('mentor/mentor_projects.html', **content)

    def post(self):
        # get project id from form
        project_id = request.form.get('projectId')
        return jsonify({'success': True, 'get_id': project_id})


# add url rule for mentor matched students
mentor_bp.add_url_rule(
    '/matched_students', view_func=MentorMatchedStudents.as_view('matched_students'))


class MentorPlacement(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # query out placement info of the current mentor
        m_placement = Mentor(user_name=g.user_name,
                             mentor_id=g.mentor_id).get_placement()
        # status option for mentor to choose
        status_option = ('Not Interested', 'Confirmed')
        # create a list to store number of confirmed students for each project
        num_confirmed = []
        # get project id of the current mentor
        project_id = Mentor(g.user_name, g.mentor_id).get_project_id()
        # convert project id to a list
        select_id = [item['project_id'] for item in project_id]

        for id in project_id:
            # query out number of confirmed students for each project
            num_confirm_each = Projects(
                id['project_id']).confirm_count(id['project_id'])
            num_confirmed.append(num_confirm_each)
        # pass m_placement, status_option, confirmed number and select_id to template
        content = {
            "title": 'Mentor Placement',
            "placement": m_placement,
            "status_option": status_option,
            "num_matched": num_confirmed,
            "select_id": select_id
        }
        return render_template('mentor/mentor_projects.html', **content)

    def post(self):
        # get  project id and status from web form
        project_id = request.form.get('project_id')
        status = request.form.get('status')
        # query out number of available slots for each project
        availabilable_slots = Projects().available_slots(project_id)
        # if no available slots, set available slots to be the same as total slots
        if availabilable_slots['available_slots'] == None:
            availabilable_slots['available_slots'] = availabilable_slots['place_num']
        # if status is confirmed, update placement status
        data = {
            'student_id': request.form.get('student_id'),
            'project_id': project_id,
            'status': status
        }

        if availabilable_slots['available_slots'] > 0:
            # if available slots is greater than 0, update placement status
            Mentor(user_name=g.user_name,
                   data=data).update_placement_status(data=data)
            # send placement result to user_name
            send_from = Notification(g.user_name).findName(g.user_name)['name']
            # query out user_name of the student
            sql = 'select user_name from student where student_id = %s;'
            para = (request.form.get('student_id'),)
            # query out user_name of the student
            send_to = run_data(sql, para, fetch=1)['user_name']
            # create a notification
            notification = {
                'subject': 'Placement Status Change',
                'send_from': send_from,
                'send_to': send_to,
                'message': 'Your Placement has been confirmed, please go to your PLACEMENT to view!',
                'receive_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'unread'
            }
            # send notification to the student
            Notification(
                notification['send_from'], notification, notification['send_to'], notification['receive_date']
            ).sentMail(
                notification['send_from'], notification, notification['send_to'], notification['receive_date'])
            # update notification table
            flash("The student's placement status updated!")
            return self.get()
        # if available slots is less than 0 and status is not confirmed, update placement status
        elif availabilable_slots['available_slots'] <= 0 and status != 'Confirmed':
            Mentor(user_name=g.user_name,
                   data=data).update_placement_status(data=data)
            flash("The student's placement status updated!")
            return self.get()
        # if available slots is less than 0, then the project has been fully placed
        else:
            flash("This project has been fully placed!", 'red')
            return self.get()


# add url rule for mentor placement page
mentor_bp.add_url_rule(
    '/placement', view_func=MentorPlacement.as_view('placement'))


class MentorAddProject(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # query out all skills
        all_skills = Skills().all_skills()
        # pass all_skills to template
        content = {
            "title": 'Add Project',
            "all_skills": all_skills
        }
        return render_template('mentor/mentor_add_project.html', **content)

    def post(self):
        # pack data into a dictionary
        data = request.form.to_dict()
        # add skills to data dictionary from form list
        data['skills'] = request.form.getlist('skills')
        # add mentor id to data dictionary
        data['mentor_id'] = g.mentor_id
        # add new project to database
        AddMentor().add_project(data)
        # query out project id of the new project
        project_id = run_data('SELECT LAST_INSERT_ID()', fetch=1)
        # get new project id from the last insert id
        data['project_id'] = project_id['LAST_INSERT_ID()']
        # add skills required to database
        AddMentor().add_skills_required(data)
        # flash message and redirect to mentor projects page
        flash('New project has been added successfully!')
        return redirect(url_for('mentor.projects'))


# add url rule for mentor add project page
mentor_bp.add_url_rule(
    '/add_project', view_func=MentorAddProject.as_view('add_project'))
