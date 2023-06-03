from flask import (Blueprint, render_template, request,
                   redirect, views, g, flash, session, current_app, url_for, jsonify)
from models import *
from webforms import RegisterForm
from functools import wraps
import os
from flask_mail import Message, Mail
import hashlib
from datetime import datetime

mentor_bp = Blueprint('mentor', __name__, url_prefix='/mentor')


@mentor_bp.errorhandler(500)
def catch_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return render_template('500.html', error=e), 500
    return decorated_function


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        user_name = session.get('user_name')
        if user_name:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner


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


@mentor_bp.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole, "mentor_id": g.mentor_id, "mentor_info": g.mentor_info}


class MentorDashboard(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        mentor_info = Mentor(g.user_name).get_mentor()
        session['mentor_info'] = mentor_info
        session['mentor_id'] = mentor_info['mentor_id']
        content = {
            "title": 'Mentor Dashboard',
            "mentor_info": mentor_info
        }
        return render_template('mentor/mentor.html', **content)


mentor_bp.add_url_rule(
    '/', view_func=MentorDashboard.as_view('mentor'))


class MentorProfile(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        mentor_info = Mentor(g.user_name).get_mentor()
        session['mentor_info'] = mentor_info
        session['mentor_id'] = mentor_info['mentor_id']

        locations = Projects(g.user_name).all_locations()
        locations = [location['location'] for location in locations]
        content = {
            "title": 'Mentor Profile',
            "locations": locations,
            "mentor_info": mentor_info
        }
        return render_template('mentor/mentor_profile.html', **content)

    def post(self):
        mentor_update = request.form.to_dict()
        print(mentor_update)
        Mentor(g.user_name, ).update(mentor_update)
        flash(
            f"{mentor_update['first_name']}'s information updated successfully!")
        return self.get()


mentor_bp.add_url_rule(
    '/profile', view_func=MentorProfile.as_view('mentor_profile'))


# mentor view/update project info
class MentorProjects(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        all_skills = Skills().all_skills()
        m_projects = Mentor(g.user_name, g.mentor_id).mentor_projects()
        if m_projects == []:
            m_projects = 'No Results'
        content = {
            "title": 'Mentor Projects',
            "projects": m_projects,
            "all_skills": all_skills
        }
        return render_template('mentor/mentor_projects.html', **content)

    def post(self):
        data = {
            'project_id': request.form.get('project_id'),
            'project_title': request.form.get('project_title'),
            'project_date': request.form.get('project_date'),
            'place_num': request.form.get('place_num'),
            'skills': request.form.getlist('skills'),
            'project_sum': request.form.get('project_sum')
        }
        try:
            Projects(data=data).remove_skills(data=data)
            AddMentor().add_skills_required(data=data)
            Projects(data=data).update_project(data=data)
            flash(
                f"Project {data['project_id']} information updated successfully!")
            return self.get()
        except Exception as e:
            flash(f'Failed to update project information! {e}', 'red')
            return self.get()


mentor_bp.add_url_rule(
    '/projects', view_func=MentorProjects.as_view('projects'))


class PreferredStudent(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        project_id = Mentor(g.user_name, g.mentor_id).get_project_id()
        filter_id = [item['project_id'] for item in project_id]
        # print(filter_id)

        students = []
        skill_match = []
        num_matched = []

        for id in project_id:
            students_for_each = Projects(
                id['project_id']).students_interested(id['project_id'])
            skill_match_each = Projects(
                id['project_id']).skill_match_number(id['project_id'])
            students.append(students_for_each)
            skill_match.append(skill_match_each)
            num_match_each = Projects(
                id['project_id']).match_count(id['project_id'])
            num_matched.append(num_match_each)

        if students:
            students[0], pagination = paginate_func(students[0], per_page=6)
        # if no one select this project, page needs to be designed --- later
        else:
            pagination = None

        print(students) 
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
        data = request.form.to_dict()
        data['status'] = 'Matched'
        try:
            Mentor(user_name=g.user_name,
                   ).new_placement(data=data)
            flash(
                f"Student {data['student_id']} has been matched to project {data['project_id']}")
            return self.get()
        except Exception as e:
            flash(f'Failed to add student to project! {e}', 'red')
            return self.get()


mentor_bp.add_url_rule(
    '/students_interested', view_func=PreferredStudent.as_view('students_interested'))


class MentorMatchedStudents(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        project_id = Mentor(g.user_name, g.mentor_id).get_project_id()
        num_matched = []
        for id in project_id:
            num_match_each = Projects(
                id['project_id']).match_count(id['project_id'])
            num_matched.append(num_match_each)

        m_students = 'all'

        get_id = request.args.get('get_id')
        get_all = request.args.get('all')

        if get_id:
            m_students = Mentor(g.user_name, g.mentor_id,
                                get_id).matched_students_withajax()
            if not m_students:
                m_students = 'Empty'

        if get_all:
            m_students = Mentor(g.user_name, g.mentor_id).matched_students()
            
        print(m_students)
        content = {
            "title": 'Matched Students',
            "students_matched": m_students,
            "num_matched": num_matched
        }
        return render_template('mentor/mentor_projects.html', **content)

    def post(self):
        project_id = request.form.get('projectId')
        # print(project_id)
        return jsonify({'success': True, 'get_id': project_id})


mentor_bp.add_url_rule(
    '/matched_students', view_func=MentorMatchedStudents.as_view('matched_students'))


class MentorPlacement(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        m_placement = Mentor(user_name=g.user_name,
                             mentor_id=g.mentor_id).get_placement()
        status_option = ('Not Interested', 'Confirmed')

        num_confirmed = []
        project_id = Mentor(g.user_name, g.mentor_id).get_project_id()
        select_id = [item['project_id'] for item in project_id]

        for id in project_id:
            num_confirm_each = Projects(
                id['project_id']).confirm_count(id['project_id'])
            num_confirmed.append(num_confirm_each)

        content = {
            "title": 'Mentor Placement',
            "placement": m_placement,
            "status_option": status_option,
            "num_matched": num_confirmed,
            "select_id": select_id
        }
        return render_template('mentor/mentor_projects.html', **content)

    def post(self):

        project_id = request.form.get('project_id')
        status = request.form.get('status')
        availabilable_slots = Projects().available_slots(project_id)

        if availabilable_slots['available_slots'] == None:
            availabilable_slots['available_slots'] = availabilable_slots['place_num']
        print(availabilable_slots)

        data = {
            'student_id': request.form.get('student_id'),
            'project_id': project_id,
            'status': status
        }

        if availabilable_slots['available_slots'] > 0:
            Mentor(user_name=g.user_name,
                    data=data).update_placement_status(data=data)
            # send to user_name
            send_from = Notification(g.user_name).findName(g.user_name)['name']
            print(send_from)
            notification = {
                'subject':'Placement Status Change',
                'send_from':send_from,
                'send_to':'rgreen',
                'message':'Your Placement has been confirmed, please go to your PLACEMENT to view!',
                'receive_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status':'unread'
            }
            Notification(
                notification['send_from'],notification,notification['send_to'],notification['receive_date']
            ).sentMail(
                notification['send_from'], notification, notification['send_to'], notification['receive_date'])

            flash("The student's placement status updated!")
            return self.get()
        elif availabilable_slots['available_slots'] <= 0 and status != 'Confirmed':
            Mentor(user_name=g.user_name,
                    data=data).update_placement_status(data=data)
            flash("The student's placement status updated!")
            return self.get()
        else:
            flash("This project has been fully placed!", 'red')
            return self.get()


mentor_bp.add_url_rule(
    '/placement', view_func=MentorPlacement.as_view('placement'))




class MentorContact(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        return render_template('mentor/contact.html', title='Contact Us')

    def post(self):
        if request.method == 'POST':
            name = request.form.get('name')
            subject = request.form.get('subject')
            message = request.form.get('message')
            print(name, subject, message)
            # msg = Message(subject=subject,
            #               sender=name,
            #               message=message,
            #               recipients=[' '])
            # mail = Mail(current_app)
            # mail.send(msg)
            flash('Your message has been sent. Thank you!')
            return redirect(url_for('mentor.contact'))


mentor_bp.add_url_rule('/contact', view_func=MentorContact.as_view('contact'))


class MentorAddProject(views.MethodView):
    decorators = [login_required]

    def get(self):
        all_skills = Skills().all_skills()
        content = {
            "title": 'Add Project',
            "all_skills": all_skills
        }
        return render_template('mentor/mentor_add_project.html', **content)

    def post(self):
        data = request.form.to_dict()
        data['skills'] = request.form.getlist('skills')
        data['mentor_id'] = g.mentor_id
        AddMentor().add_project(data)
        project_id = run_data('SELECT LAST_INSERT_ID()', fetch=1)
        data['project_id'] = project_id['LAST_INSERT_ID()']
        AddMentor().add_skills_required(data)
        flash('New project has been added successfully!')
        return redirect(url_for('mentor.projects'))


mentor_bp.add_url_rule(
    '/add_project', view_func=MentorAddProject.as_view('add_project'))
