from flask import Flask, render_template, request, views, session, redirect, url_for, flash, g, flash
from webforms import LoginForm, RegisterForm, SearchForm, NoticeForm
from mentor.mentor_view import *
from staff.staff_view import *
from student.student_view import *
from models import *
from functools import wraps
import hashlib
from flask import jsonify
from flask_mail import Mail, Message
import random
from flask_moment import Moment

# set up flask app
app = Flask(__name__)
# secret key for the session
app.secret_key = "secret"
# secret key for the wtform
app.config['SECRET_KEY'] = 'This_is_the_secret_key'

# import blueprints defined in other files
app.register_blueprint(staff_bp)
app.register_blueprint(mentor_bp)
app.register_blueprint(student_bp)

# set moment class for flask-moment
moment = Moment(app)


# flask_mail setup
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "rpwin1314@gmail.com"
app.config['MAIL_PASSWORD'] = "vsxvbkqpqruoqtwy"
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)

# define catch exception func and return 500 page


def catch_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return render_template('500.html', error=e), 500
    return decorated_function

# set global variables by using before_request hook


@app.before_request
def my_before_request():
    # get user info from session
    user_name = session.get('user_name')
    userrole = session.get('userrole')
    avatar_link = session.get('avatar_link')
# set global variables
    if user_name:
        setattr(g, 'user_name', user_name)
        setattr(g, 'userrole', userrole)
        setattr(g, 'avatar_link', avatar_link)
    else:
        setattr(g, 'user_name', None)
        setattr(g, 'userrole', None)
        setattr(g, 'avatar_link', None)


# push context to all pages
@app.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole}


# decorators to verify login status
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # if user is logged in, return the function
        user_name = session.get('user_name')
        if user_name:
            return func(*args, **kwargs)
        else:
            # if user is not logged in, redirect to login page
            return redirect(url_for('login'))
    return inner


# define index page
@app.route('/', methods=['POST', 'GET'])
@catch_exception
def index():
    return render_template('index.html', title='Welcome')


# class view method to define log-in page
class LoginView(views.MethodView):
    # add decorators to catch exception
    decorators = [catch_exception]

    def get(self):
        # if user is logged in, redirect to corresponding page
        userrole = session.get('userrole')
        if userrole == 'student':
            return redirect('/student')
        elif userrole == 'mentor':
            return redirect('/mentor')
        elif userrole == 'staff':
            return redirect('/staff')
        else:
            form = LoginForm()
            return render_template('login.html', title='Login', form=form)

# if user is logged in, redirect to corresponding page
    def post(self):
        # use wtform to validate input
        form = LoginForm()

        if form.validate_on_submit():
            user_name = form.user_name.data
            password = form.password.data
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            # if input is valid, check if user name and password match
            result = User(user_name).check_password()
# check if user name and password match
            if result:
                if result['password'] == password:
                    session['userrole'] = result['role']
                    session['user_name'] = user_name
                    avatar_link = User(user_name).get_avatar(
                        user_name)[0]['link']
# if user has not set avatar, use default avatar
                    if not avatar_link:
                        avatar_link = '../static/avatar/test.png'
# save user avatar link to session
                    session['avatar_link'] = avatar_link
# direct to corresponding page according to user role
                    if session['userrole'] == 'student':
                        return redirect('/student')
                    elif session['userrole'] == 'mentor':
                        return redirect('/mentor')
                    elif session['userrole'] == 'staff':
                        return redirect('/staff')

                else:
                    flash('Information you input is not valid.', 'red')
                    return self.get()
            else:
                flash('Information you input is not valid.', 'red')
                return self.get()
        else:
            flash('form validate error', 'red')
            return render_template('login.html', title='Welcome', form=form)


# add url rule for login page
app.add_url_rule('/login', view_func=LoginView.as_view('login'))

# method view for forget password


class ForgetPassword(views.MethodView):
    # add decorators to catch exception
    decorators = [catch_exception]

    def get(self):
        return render_template('forget_password.html')
# generate random integer for temparory password

    def post(self):
        user_name = request.form.get('user_name1')
        email = request.form.get('email')
        # check if user name and email address match
        result = User(user_name).check_password()
        if result:
            userrole = result['role']
            email_code = generate_randomint()
        # update hashed temparory password to database
            password_new = hashlib.sha256(
                email_code.encode('utf-8')).hexdigest()
            User(user_name, password_new).update_password()
# send email to user with temparory password
            msg_title = "Forget Password"
            sender = "noreply@app.com"
            msg = Message(msg_title, sender=sender, recipients=[
                          f'{email}'], body=f"Your new password is {email_code}")
# try to send email, if failed, return error message
            try:
                mail.send(msg)
                flash(
                    'A Temparory password has been sent to your email address, please change your password ASAP')
                session['user_name'] = user_name
                session['userrole'] = userrole
                return redirect('/login')
            except Exception as e:
                return f"email was not sent{e}"
        else:
            flash('This user_name does not exit.', 'red')
            return self.get()


app.add_url_rule('/password',
                 view_func=ForgetPassword.as_view('password'))


# change password page
class ChangePassword(views.MethodView):
    # require login and catch exception
    decorators = [login_required]
    decorators = [catch_exception]

    def get(self):
        context = {}
# check user role and add corresponding information to context
        if g.userrole == 'student':
            context['student_info'] = session['student_info']
        elif g.userrole == 'staff':
            context['staff_info'] = session['staff_info']
        elif g.userrole == 'mentor':
            context['mentor_info'] = session['mentor_info']

        return render_template('/student/change_password.html', **context)
# save new password to database

    def post(self):
        newpassword = request.form.get('newpassword')
        if newpassword:
            user_code = request.form.get('code')
            # add salt and hash to password
            newpassword = hashlib.sha256(
                newpassword.encode('utf-8')).hexdigest()
            # print(session.get('who')['code'])
            if user_code == session.get('who')['code']:
                # update password to database
                User(g.user_name, newpassword).update_password()
                # delete session
                session.pop('who')
                flash('Password has been changed successfully')
                return redirect(url_for('login'))
            else:
                flash('Wrong verification code, please enter again', 'red')
                return self.get()
        else:
            # get email address from form submission
            email = request.form.get('email')
            # generate random integer for verification code
            email_code = generate_randomint()
            # save email address and verification code to session
            session['who'] = {
                'email': email,
                'code': email_code
            }
            sender = "noreply@app.com"
            # send email to user with verification code
            msg = Message('change password', sender=sender, recipients=[
                          f'{email}'], body=f"Your verification code is {email_code}")
            current_app.extensions.get('mail').send(msg)
            return self.get()


app.add_url_rule(
    '/change_password/', view_func=ChangePassword.as_view('change_password'))


class UpdateAvatar(views.MethodView):
    def get(self):

        pass

    def post(self):
        # get the uploaded file
        avatar = request.files.get('avatar')
        # os module to get the path of the current file
        base_path = os.path.dirname(os.path.abspath(__name__))
        str_path = r"/static/avatar/"
        # save the uploaded file to the static/avatar folder
        upload_path = base_path + str_path + avatar.filename
        avatar.save(upload_path)
        # save the path of the uploaded file to the database
        database_path = "/static/avatar/" + avatar.filename
        session_path = "../static/avatar/" + avatar.filename
        # update the avatar path in the database for the current user
        User(g.user_name, database_path=database_path).update_avatar(
            g.user_name, database_path=database_path)
        # update the avatar path in the session for the current user
        session['avatar_link'] = session_path
        # get the url link of the current page
        url_link = request.referrer
        # remove the host name from the url link
        url_link = url_link.split('http://127.0.0.1:5000')[1]
        flash('Your profile picture is updated')
        return redirect(f'{url_link}')


# add the url rule for the update avatar page
app.add_url_rule(
    '/update_avatar/', view_func=UpdateAvatar.as_view('update_avatar'))

# send notification page


class SendNotification(views.MethodView):
    decorators = [login_required]

    def get(self):
        form = NoticeForm()
        # query the notification data from the database
        sql = '''select * from notification where send_to = %s order by receive_date Desc;'''
        para = (g.user_name,)
        results = run_data(sql, para, fetch=2)
        # get the user_name of the receiver from the url
        send_to = request.args.get('send_to')
        if send_to:
            # query the name of the receiver
            send_to = Notification(user_name=send_to).findName(
                user_name=send_to)['name']
            return render_template('/send_notice.html', form=form, results=results, send_to=send_to)

        return render_template('/send_notice.html', form=form, results=results)

    def post(self):
        # get the data from the form
        data = request.form.to_dict()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name_search = data['send_to']
        # query the user_name of the receiver
        user_name_search = Notification(
            name=name_search).searchUsername(name=name_search)
        # if the receiver does not exist, return error message
        if not user_name_search:
            flash('The receiver does not exist, please enter again!', 'red')
            return self.get()
        else:
            user_name_search = user_name_search['user_name']
        # send the notification to the receiver's inbox
        Notification(g.user_name, data=data, send_to=user_name_search, current_time=current_time).sentMail(
            g.user_name, data=data, send_to=user_name_search, current_time=current_time)

        flash('Message has been sent successfully')
        return self.get()


app.add_url_rule(
    '/send_notice/', view_func=SendNotification.as_view('send_notice'))


class NoticeControl(views.MethodView):
    decorators = [login_required]

    def get(self):
        # query the notification data from the database
        notice_id = request.args.get('notice_id')
        status = request.args.get('status')
        if status == 'unread':
            # update the status of the notification to read
            sql = '''update notification set status = "read" where notification_id = %s'''
            para = (notice_id,)
            run_data(sql, para)
            return redirect(url_for('send_notice'))
        else:
            return redirect(url_for('send_notice'))

    def post(self):
        data = request.form.to_dict()
        return 'ok'


app.add_url_rule(
    '/notice_control/', view_func=NoticeControl.as_view('notice_control'))


class SearchUser(views.MethodView):
    decorators = [login_required]

    def get(self):
        # query the name of all users
        send_to_name = Notification().searchName()
        # get the name of the users
        send_to_name = [name['name'] for name in send_to_name]
        # get the search text from the url
        search_text = request.args.get('search', '')
        # get the names that match the search text
        matching_names = [
            name for name in send_to_name if name.lower().startswith(search_text.lower())]
        # if there is no matching names, return 'No Match results'
        if not matching_names:
            matching_names = ['No Match results']
        return jsonify({'names': matching_names})


app.add_url_rule(
    '/search_user/', view_func=SearchUser.as_view('search_user'))

# define error page


@app.errorhandler(404)
def error_control(error):
    return render_template('404.html', title='404', error=error)

# logout route


@app.route('/logout', methods=['POST', 'GET'])
@catch_exception
def logout():
    session.clear()
    return redirect(url_for('login'))


# run the app and config debug mode
if __name__ == '__main__':
    app.run(debug=True)
