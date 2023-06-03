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


app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "rpwin1314@gmail.com"
app.config['MAIL_PASSWORD'] = "vsxvbkqpqruoqtwy"
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)


# errorhandler
@student_bp.errorhandler(500)
def catch_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return render_template('500.html', error=e), 500
    return decorated_function

# student register view


@student_bp.before_request
def my_before_request():
    user_name = session.get('user_name')
    userrole = session.get('userrole')
    student_info = session.get('student_info')
    Avatar_link = session.get('Avatar_link')

    if user_name:
        setattr(g, 'user_name', user_name)
        setattr(g, 'userrole', userrole)
        setattr(g, 'student_info', student_info)
        setattr(g, 'Avatar_link', Avatar_link)
    else:
        setattr(g, 'user_name', None)
        setattr(g, 'userrole', None)
        setattr(g, 'student_info', None)
        setattr(g, 'Avatar_link', None)


@student_bp.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole, "student_info": g.student_info}


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        user_name = session.get('user_name')
        if user_name:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner


class StudentDashboard(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        student_info = Student(g.user_name).get_student()

        Avatar_link = User(g.user_name).get_avatar(g.user_name)[0]['link']

        if not Avatar_link:
            Avatar_link = '../static/avatar/test.png'

        session['Avatar_link'] = Avatar_link
        g.Avatar_link = Avatar_link

        session['student_info'] = student_info
        content = {
            "title": 'Student Dashboard',
            "student_info": student_info,
            "g.Avatar_link": g.Avatar_link
        }
        return render_template('student/student.html', **content)


student_bp.add_url_rule(
    '/', view_func=StudentDashboard.as_view('student'))


class StudentProfile(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        all_skills = Skills().all_skills()
        student_info = Student(g.user_name).get_student()
        # print(student_info)
        student_id = student_info['student_id']
        placement_info = Student(student_id).get_placement()
        locations = Projects().all_locations()
        cv_link = Student(g.user_name).cv_link()['cv_link']
        # print(cv_link)

        if placement_info:
            placement_info = placement_info['status']
        else:
            placement_info = 'No Placement'
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

        if not cv_link:
            database_path = None
            student_update['cv_link'] = 'None'
        else:
            base_path = os.path.dirname(os.path.abspath(__name__))
            str_path = r"/static/cv_folder/"
            upload_path = base_path + str_path + cv_link.filename
            cv_link.save(upload_path)
            database_path = "/static/cv_folder/" + cv_link.filename
            student_update['cv_link'] = f'{database_path}'

        Student(g.user_name, student_update=student_update).update(
            student_update)
        flash(
            f"{student_update['first_name']} Personal Details Updated Successfully!")

        return redirect(url_for('student.student_profile'))


student_bp.add_url_rule(
    '/profile', view_func=StudentProfile.as_view('student_profile'))


class StudentWishlist(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        student_id = g.student_info['student_id']
        student = Student(g.user_name, student_id=student_id)
        wishlist_info = student.get_wishlist()
        # print(wishlist_info)
        wishlist_status = student.wishlist_status()
        # print(wishlist_status)
        # empty = 0

        content = {
            'title': 'Student Wishlist',
            'wishlist_info': wishlist_info,
            'wishlist_status': wishlist_status
        }

        if not wishlist_info and not wishlist_status:
            content['empty'] = 1

        return render_template('student/wishlist.html', **content)

    def post(self):
        # receive project_id and ranking
        selected_id = request.form.getlist('wishlist[]')
        option = request.form.getlist('ranking[]')
        data = dict(zip(selected_id, option))
        # print(data)
        for key, value in data.items():
            WishiList().update_project(
                key, g.student_info['student_id'], ranking=value)

        print('success')
        flash('Wishlist has been sumitted successfully')
        return self.get()


student_bp.add_url_rule(
    '/wishlist', view_func=StudentWishlist.as_view('wishlist'))


class WishlistControl(views.MethodView):
    decorators = [login_required]

    def get(self):
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
        # if submit:
        #     sql = '''update wishlist set submission_status = %s where project_id=%s and student_id=%s;'''
        #     if submit == '1':
        #         para = ('Submitted', project_id, student_id)
        #     elif submit == '2':
        #         para = ('Drafted', project_id, student_id)

        #     run_data(sql, para)
        #     flash(f"Project ID: {project_id} status has been changed")
        #     return redirect(url_for('student.wishlist'))

    def post(self):

        pass


student_bp.add_url_rule(
    '/wishlist_control', view_func=WishlistControl.as_view('wishlist_control'))


class UpdateWishlist(views.MethodView):
    decorators = [login_required]

    def get(self):
        student_id = g.student_info['student_id']
        project_id = request.args.get('project_id')
        # print(project_id)
        remove = request.args.get('remove')

        if remove:
            WishiList().remove_project(project_id, student_id)
            flash(
                f"Project {project_id} has been removed from your wishlist")
            return redirect(url_for('student.all_projects'))
        else:
            WishiList().add_project(project_id, student_id)
            flash(
                f"Project {project_id} has been added to wishlist successfully!")
            return redirect(url_for('student.all_projects'))


student_bp.add_url_rule(
    '/wishlist_update', view_func=UpdateWishlist.as_view('wishlist_update'))


class AllProjects(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self, data=None):

        all_projects = Projects(g.student_info['student_id'])
        project_detail = {}

        detail_flag = request.args.get('detail')
        if detail_flag:
            project_id = request.args.get('project_id')
            project_detail = all_projects.projects_details(project_id)

        projects = all_projects.all_projects()

        if data:
            projects = Projects(data=data).filter_projects(data)

        # simon modify page layout, add pagination func, 3 items per page
        projects, pagination = paginate_func(projects, per_page=6)

        selected_project = all_projects.selected_projects(
            g.student_info['student_id'])

        projects_submitted = Projects(g.student_info['student_id']).projects_submitted(
            g.student_info['student_id'])

        # this can be userful in passing parameters into html
        content = {
            'title': 'All Projects',
            'projects': projects,
            "pagination": pagination,
            'selected_project': selected_project,
            'project_detail': project_detail,
            'projects_submitted': projects_submitted
        }

        if projects == []:
            flash('No data found, Please re-enter keywords.', 'red')

        return render_template('student/all_projects.html', **content)

    # post method for filter
    def post(self):
        data = request.form.to_dict()
        return self.get(data)


student_bp.add_url_rule(
    '/all_projects', view_func=AllProjects.as_view('all_projects'))


# route for student to add their own project which not scheduled by school
class StudentAddProject(views.MethodView):
    def get(self):
        all_skills = Skills().all_skills()
        content = {
            "title": 'Add Project',
            "all_skills": all_skills
        }
        return render_template('student/add_project.html', **content)

    def post(self):
        data = request.form.to_dict()
        data['skills'] = request.form.getlist('skills')
        m_username = data['first_name'].lower() + data['last_name'][0].lower()
        data['user_name'] = m_username

        AddMentor().generate_username(data)

        password = '1111'
        data['password'] = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # print(data)
        AddMentor().add_user(data)
        AddMentor().add_mentor(data)
        mentor_id = run_data('SELECT LAST_INSERT_ID()', fetch=1)
        data['mentor_id'] = mentor_id['LAST_INSERT_ID()']
        AddMentor().add_project(data)
        project_id = run_data('SELECT LAST_INSERT_ID()', fetch=1)
        data['project_id'] = project_id['LAST_INSERT_ID()']
        AddMentor().add_skills_required(data)
        data['student_id'] = g.student_info['student_id']
        AddMentor().add_placement(data)
        flash('Your own project being added successfully!')
        return redirect(url_for('student.placement'))


student_bp.add_url_rule(
    '/add_project', view_func=StudentAddProject.as_view('add_project'))


class StudentPlacement(views.MethodView):
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        student_id = g.student_info['student_id']
        placements = Student(g.user_name, student_id).get_placement()

        wishlist_info = Student(
            g.user_name, student_id=student_id).get_wishlist()
        wishlist_status = Student(
            g.user_name, student_id=student_id).wishlist_status()

        if placements:
            placements = placements[0]
            placements['status'] = "Matched"
        if not placements and not wishlist_status:
            placements = {'status': 'No Placements'}
        elif not placements and wishlist_status:
            placements = {'status': 'Processing'}
        print(placements)
        content = {
            'title': 'My placement',
            'placements': placements,
            'status_list': ['No Placements', "Processing", 'Matched']
        }
        return render_template('student/wishlist.html', **content)


student_bp.add_url_rule(
    '/placement', view_func=StudentPlacement.as_view('placement'))


class StudentRegister(views.MethodView):

    def get(self):
        form = RegisterForm()
        content = {
            "title": 'Student Registration',
            "form": form
        }
        return render_template('student/register.html', **content)

    def post(self):
        form = RegisterForm()
        if form.validate_on_submit():
            skills = request.form.getlist('skills')
            need_project = request.form.get('need_project')
            # print(need_project)
            result = request.form.to_dict()
            result['password'] = hashlib.sha256(
                result['password'].encode('utf-8')).hexdigest()
            cv_link = request.files.get('cv')
            result['skills'] = skills

            if not cv_link:
                database_path = None
                result['cv_link'] = 'None'
            else:
                base_path = os.path.dirname(os.path.abspath(__name__))
                str_path = r"/static/cv_folder/"
                upload_path = base_path + str_path + cv_link.filename
                cv_link.save(upload_path)
                database_path = "/static/cv_folder/" + cv_link.filename
                result['cv_link'] = f'{database_path}'

            # save into database

            User(result['user_name'],
                 password_new=result['password']).add_user()
            NewStudent(result).add_student(result)
            NewStudent(result).add_student_skill(result)

            msg_title = "Welcome new user"
            sender = "noreply@app.com"
            email = result['email']
            msg = Message(msg_title, sender=sender, recipients=[
                          f'{email}'], body=f"Your password is '1111', username is {result['user_name']}")
            try:
                mail.send(msg)
                flash('Registered successfully! Welcome!')

                session['user_name'] = result['user_name']
                session['userrole'] = 'student'

                if need_project == '0':
                    return redirect(url_for('student.add_project'))
                return redirect(url_for('login'))

            except Exception as e:
                flash('Failed to send email to address', 'red')
                return self.get()
        else:
            print(form.errors)
            errors = form.errors.popitem()[1][0]
            flash(f' {errors}. Please try again!', 'red')
            form = RegisterForm()
            return render_template('student/register.html', title='Student Registration', form=form)


student_bp.add_url_rule(
    '/register/', view_func=StudentRegister.as_view('student_register'))
