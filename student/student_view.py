from flask import (Flask, Blueprint, render_template, request,
                   redirect, views, g, flash, session, current_app, url_for,)
from models import *
from webforms import RegisterForm
from functools import wraps
import os
from flask_mail import Message, Mail
import hashlib
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)

# set up student blueprint
student_bp = Blueprint('student', __name__, url_prefix='/student')

# config mail server for sending email
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "rpwin1314@gmail.com"
app.config['MAIL_PASSWORD'] = "vsxvbkqpqruoqtwy"
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)


# create error handler for  500
@student_bp.errorhandler(500)
def catch_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return render_template('500.html', error=e), 500
    return decorated_function


# store user info in g
@student_bp.before_request
def my_before_request():
    # get user info from session
    user_name = session.get('user_name')
    userrole = session.get('userrole')
    student_info = session.get('student_info')
    avatar_link = session.get('avatar_link')
    # store user info in g
    if user_name:
        setattr(g, 'user_name', user_name)
        setattr(g, 'userrole', userrole)
        setattr(g, 'student_info', student_info)
        setattr(g, 'avatar_link', avatar_link)
    else:
        setattr(g, 'user_name', None)
        setattr(g, 'userrole', None)
        setattr(g, 'student_info', None)
        setattr(g, 'avatar_link', None)

# set up context processor for jinja2 template


@student_bp.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole, "student_info": g.student_info}

# define login required decorator


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        user_name = session.get('user_name')
        if user_name:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner

# class view for student dashboard


class StudentDashboard(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # query student info from database
        student_info = Student(g.user_name).get_student()
        # query avatar link path from database
        avatar_link = User(g.user_name).get_avatar(g.user_name)[0]['link']
        # if avatar link is empty, use default avatar
        if not avatar_link:
            avatar_link = '../static/avatar/test.png'
        # store avatar link in session
        session['avatar_link'] = avatar_link
        g.avatar_link = avatar_link
        # store student info in session
        session['student_info'] = student_info
        # render content data to student dashboard template
        content = {
            "title": 'Student Dashboard',
            "student_info": student_info,
            "g.avatar_link": g.avatar_link
        }
        return render_template('student/student.html', **content)


# add url rule for student dashboard
student_bp.add_url_rule(
    '/', view_func=StudentDashboard.as_view('student'))

# class view for student profile


class StudentProfile(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # query all skills from database
        all_skills = Skills().all_skills()
        # query student info from database
        student_info = Student(g.user_name).get_student()
        # get student id from student info
        student_id = student_info['student_id']
        # query placement info from database
        placement_info = Student(student_id).get_placement()
        # query all locations from database
        locations = Projects().all_locations()
        # query cv link from database
        cv_link = Student(g.user_name).cv_link()['cv_link']
        #  if there is a placement info, get the status
        if placement_info:
            placement_info = placement_info['status']
        else:
            # if there is no placement info, set status to 'No Placement'
            placement_info = 'No Placement'
            # render content data to student profile template
        context = {
            'title': 'Student Profile',
            'student_info': student_info,
            'placement_info': placement_info,
            'locations': locations,
            'all_skills': all_skills,
            'cv_link': cv_link
        }
        return render_template('student/student_profile.html', **context)

    def post(self):
        # update student info
        student_update = request.form.to_dict()
        cv_link = request.files.get('cv_link')
        # validate email address and it can be the same as the old one
        if VerificationMethod(g.user_name, student_update['email']).verify_email_student(g.user_name, student_update['email']):
            flash('Email address Exists', 'red')
            return self.get()
        # if cv link is empty, set cv link to None
        if not cv_link:
            database_path = None
            student_update['cv_link'] = 'None'
        else:
            # if cv link is not empty, save cv link to static folder
            base_path = os.path.dirname(os.path.abspath(__name__))
            # base path for static folder
            str_path = r"/static/cv_folder/"
            # upload path for cv link
            upload_path = base_path + str_path + cv_link.filename
            # save cv file to static folder
            cv_link.save(upload_path)
            # save cv link to database
            database_path = "/static/cv_folder/" + cv_link.filename
            # store cv link in student database
            student_update['cv_link'] = f'{database_path}'
        # update student info in database
        Student(g.user_name, student_update=student_update).update(
            student_update)
        # flash message once student info is updated
        flash(
            f"{student_update['first_name']} Personal Details Updated Successfully!")
        # redirect to student profile page
        return redirect(url_for('student.student_profile'))


# add url rule for student profile
student_bp.add_url_rule(
    '/profile', view_func=StudentProfile.as_view('student_profile'))

# class view for student placement


class StudentWishlist(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get student id from session
        student_id = g.student_info['student_id']
        # define student object
        student = Student(g.user_name, student_id=student_id)
        # get wishlist info from database
        wishlist_info = student.get_wishlist()
        # query wishlist status from database
        wishlist_status = student.wishlist_status()
        # render content data to student wishlist template
        content = {
            'title': 'Student Wishlist',
            'wishlist_info': wishlist_info,
            'wishlist_status': wishlist_status
        }
        # if wishlist info and wishlist status are empty, set empty to 1
        if not wishlist_info and not wishlist_status:
            content['empty'] = 1
        # render student wishlist template
        return render_template('student/wishlist.html', **content)

    def post(self):
        # receive project_id and ranking
        selected_id = request.form.getlist('wishlist[]')
        # get the ranking option from form
        option = request.form.getlist('ranking[]')
        # zip project_id and ranking option together
        data = dict(zip(selected_id, option))
        #  get the items from data, set the key as project_id, value as ranking and update to wishlist database
        for key, value in data.items():
            WishiList().update_project(
                key, g.student_info['student_id'], ranking=value)
        #  flash message once wishlist is submitted
        flash('Wishlist has been sumitted successfully')
        return self.get()


# add url rule for student wishlist
student_bp.add_url_rule(
    '/wishlist', view_func=StudentWishlist.as_view('wishlist'))

# class view for student placement


class WishlistControl(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get the project id, student idfrom url
        remove = request.args.get('remove')
        project_id = request.args.get('project_id')
        student_id = g.student_info['student_id']

      # remove/change status of wishilist item from database
        if remove:
            WishiList().remove_project(project_id, student_id)
            flash(
                f"Project ID: {project_id} has been removed from your wishlist")
            return redirect(url_for('student.wishlist'))
        else:
            pass


# add url rule for student wishlist control
student_bp.add_url_rule(
    '/wishlist_control', view_func=WishlistControl.as_view('wishlist_control'))

# class view for student placement


class UpdateWishlist(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get the project id, student id from url
        student_id = g.student_info['student_id']
        project_id = request.args.get('project_id')
        remove = request.args.get('remove')
        if remove:
            # if remove is true, remove the project from wishlist
            WishiList().remove_project(project_id, student_id)
            flash(
                f"Project {project_id} has been removed from your wishlist")
            return redirect(url_for('student.all_projects'))
        else:
            # if remove is false, add the project to wishlist
            WishiList().add_project(project_id, student_id)
            flash(
                f"Project {project_id} has been added to wishlist successfully!")
            return redirect(url_for('student.all_projects'))


#  add url rule for student wishlist update
student_bp.add_url_rule(
    '/wishlist_update', view_func=UpdateWishlist.as_view('wishlist_update'))


class AllProjects(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self, data=None):
        # get all projects from database
        all_projects = Projects(g.student_info['student_id'])
        # set an empty dict for project detail
        project_detail = {}
        # get the detail flag from url
        detail_flag = request.args.get('detail')
        if detail_flag:
            # if detail flag is true, get the project detail from database
            project_id = request.args.get('project_id')
            project_detail = all_projects.projects_details(project_id)
        # get all projects from database
        projects = all_projects.all_projects()

        if data:
            # if data is not empty, filter the projects by keywords
            projects = Projects(data=data).filter_projects(data)

        # modified page layout, add pagination func, 3 items per page
        projects, pagination = paginate_func(projects, per_page=6)
        # query out the selected projects from database
        selected_project = all_projects.selected_projects(
            g.student_info['student_id'])
        # query the submitted  wishlist from database
        projects_submitted = Projects(g.student_info['student_id']).projects_submitted(
            g.student_info['student_id'])

        # pass parameters to all projects html template
        content = {
            'title': 'All Projects',
            'projects': projects,
            "pagination": pagination,
            'selected_project': selected_project,
            'project_detail': project_detail,
            'projects_submitted': projects_submitted
        }
        # if projects is empty, flash message
        if projects == []:
            flash('No data found, Please re-enter keywords.', 'red')

        return render_template('student/all_projects.html', **content)

    # post method for filter
    def post(self):
        # get the interest flag from web form
        interest = request.form.get('interest')
        if interest:
            # if interest flag is true, get the projects info from database
            location = request.form.get('location')
            industry = request.form.get('industry')
            skills = request.form.get('skills')
            # set the data as a dict
            data = {
                'location': location,
                'industry': industry,
                'skills': skills,
                'name': None
            }
        else:
            data = request.form.to_dict()
        # return the get method with data
        return self.get(data)


#  add url rule for student all projects
student_bp.add_url_rule(
    '/all_projects', view_func=AllProjects.as_view('all_projects'))


# route for student to add their own project which not scheduled by school
class StudentAddProject(views.MethodView):
    def get(self):
        # get all skills from database
        all_skills = Skills().all_skills()
        # pass parameters to add project html template
        content = {
            "title": 'Add Project',
            "all_skills": all_skills
        }
        return render_template('student/add_project.html', **content)

    def post(self):
        # pack the data from web form as a dict
        data = request.form.to_dict()
        # get the skills list from web form
        data['skills'] = request.form.getlist('skills')
        # generate the mentor's username from first name and last name
        m_username = data['first_name'].lower() + data['last_name'][0].lower()
        # store the username in data dict
        data['user_name'] = m_username
        # add the mentor's username to database
        AddMentor().generate_username(data)
        #  give the mentor a default password
        password = '1111'
        # add salt and hash to the password
        data['password'] = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # add the mentor's info to user table in database
        AddMentor().add_user(data)
        # add mentor info to mentor table in database
        AddMentor().add_mentor(data)
        # get mentor id from last insert query
        mentor_id = run_data('SELECT LAST_INSERT_ID()', fetch=1)
        # store the mentor id in data dict
        data['mentor_id'] = mentor_id['LAST_INSERT_ID()']
        # add new project and mentor id to project table in database
        AddMentor().add_project(data)
        # get project id from last insert query
        project_id = run_data('SELECT LAST_INSERT_ID()', fetch=1)
        # store the project id in data dict
        data['project_id'] = project_id['LAST_INSERT_ID()']
        # add skills required to project_skill table in database
        AddMentor().add_skills_required(data)
        # store the student id in data dict
        data['student_id'] = g.student_info['student_id']
        # add the project and student information into placement table in database
        AddMentor().add_placement(data)
        # flash message once the student's project being added successfully and redirect to student placement page
        flash('Your own project being added successfully!')
        return redirect(url_for('student.placement'))


# add url rule for student add project
student_bp.add_url_rule(
    '/add_project', view_func=StudentAddProject.as_view('add_project'))

# class view for student to view their own placement


class StudentPlacement(views.MethodView):
    decorators = [login_required, catch_exception]

    def get(self):
        # get the student id from session
        student_id = g.student_info['student_id']
        # qyery the student's placement info from database
        placements = Student(g.user_name, student_id).get_placement()

        # query the student's wishlist status from database
        wishlist_status = Student(
            g.user_name, student_id=student_id).wishlist_status()

        if placements:
            # if placements is not empty, get the project info from database
            placements = placements[0]
            placements['status'] = "Matched"
        if not placements and not wishlist_status:
            # if placements and wishlist_status are both empty, set the status as 'No Placements'
            placements = {'status': 'No Placements'}
        elif not placements and wishlist_status:
            # if placements is empty and wishlist_status is not empty, set the status as 'Processing'
            placements = {'status': 'Processing'}
        # pass parameters to wishlist html template
        content = {
            'title': 'My placement',
            'placements': placements,
            'status_list': ['No Placements', "Processing", 'Matched']
        }
        return render_template('student/wishlist.html', **content)


# add url rule for student placement
student_bp.add_url_rule(
    '/placement', view_func=StudentPlacement.as_view('placement'))

# class view for student to register their account


class StudentRegister(views.MethodView):

    def get(self):
        # render wtf from to web page
        form = RegisterForm()
        # pass parameters to register html template
        content = {
            "title": 'Student Registration',
            "form": form
        }
        # render the register html template
        return render_template('student/register.html', **content)

    def post(self):
        # render the wtf form to web page
        form = RegisterForm()
        # get the data from web form
        if form.validate_on_submit():
            # get student skills list from web form
            skills = request.form.getlist('skills')
            # get the value of need_project from web form
            need_project = request.form.get('need_project')
            # pack the data from web form as a dict
            result = request.form.to_dict()
            # add salt and hash to the password
            result['password'] = hashlib.sha256(
                result['password'].encode('utf-8')).hexdigest()
            # get the cv link from web form
            cv_link = request.files.get('cv')
            # store the cv link in data dict
            result['skills'] = skills
            # if the student doesn't have a cv, set the cv link as None
            if not cv_link:
                database_path = None
                result['cv_link'] = 'None'
            else:
                # save the cv file into static folder
                base_path = os.path.dirname(os.path.abspath(__name__))
                # base path to store all the cv files
                str_path = r"/static/cv_folder/"
                # the path of the cv file
                upload_path = base_path + str_path + cv_link.filename
                # save the cv file into the path
                cv_link.save(upload_path)
                # store the cv link in data dict
                database_path = "/static/cv_folder/" + cv_link.filename
                # store the cv link in data dict
                result['cv_link'] = f'{database_path}'

            # save into database
            User(result['user_name'],
                 password_new=result['password']).add_user()
            # add student info to student table in database
            NewStudent(result).add_student(result)
            # add student skills to student_skill table in database
            NewStudent(result).add_student_skill(result)
            #  make message title and sender
            msg_title = "Welcome new user"
            sender = "noreply@app.com"
            email = result['email']
            # send message to student by email to notify them their username and password
            msg = Message(msg_title, sender=sender, recipients=[
                          f'{email}'], body=f"Your password is '1111', username is {result['user_name']}")
            try:
                #  try to send email
                mail.send(msg)
                flash('Registered successfully! Welcome!')
                # store the student username in session
                session['user_name'] = result['user_name']
                # store the student role in session
                session['userrole'] = 'student'

                if need_project == '0':
                    # if the student have a project, redirect to student home page
                    return redirect(url_for('student.add_project'))
                return redirect(url_for('login'))

            except Exception as e:
                # if failed to send email, flash message and redirect to register page
                flash('Failed to send email to address', 'red')
                return self.get()
        else:
            # if the form is not valid, flash message and redirect to register page
            errors = form.errors.popitem()[1][0]
            flash(f' {errors}. Please try again!', 'red')
            # rerender the register html template
            form = RegisterForm()
            return render_template('student/register.html', title='Student Registration', form=form)


# add url rule for student register
student_bp.add_url_rule(
    '/register/', view_func=StudentRegister.as_view('student_register'))
