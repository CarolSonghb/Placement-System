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


def catch_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return render_template('500.html', error=e), 500
    return decorated_function


@app.before_request
def my_before_request():
    user_name = session.get('user_name')
    userrole = session.get('userrole')
    Avatar_link = session.get('Avatar_link')

    if user_name:
        setattr(g, 'user_name', user_name)
        setattr(g, 'userrole', userrole)
        setattr(g, 'Avatar_link', Avatar_link)
    else:
        setattr(g, 'user_name', None)
        setattr(g, 'userrole', None)
        setattr(g, 'Avatar_link', None)


# push context to all pages
@app.context_processor
def my_context_processor():
    return {"user_name": g.user_name, "userrole": g.userrole}


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


@app.route('/', methods=['POST', 'GET'])
@catch_exception
def index():
    return render_template('index.html', title='Welcome')


# class view method to define log-in page
class LoginView(views.MethodView):
    decorators = [catch_exception]

    def get(self):
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

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            user_name = form.user_name.data
            password = form.password.data
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            result = User(user_name).check_password()

            if result:
                if result['password'] == password:
                    session['userrole'] = result['role']
                    session['user_name'] = user_name

                    # sql = '''select link from user where user_name = %s'''
                    # para = (user_name,)
                    # Avatar_link = run_data(sql, para, fetch=2)[0]['link']
                    Avatar_link = User(user_name).get_avatar(
                        user_name)[0]['link']

                    if not Avatar_link:
                        Avatar_link = '../static/avatar/test.png'

                    session['Avatar_link'] = Avatar_link

                    print('ok')
                    print(session['Avatar_link'])
                    print('ok')

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


app.add_url_rule('/login', view_func=LoginView.as_view('login'))


class ForgetPassword(views.MethodView):
    decorators = [catch_exception]

    def get(self):
        return render_template('forget_password.html')

    def post(self):
        user_name = request.form.get('user_name1')
        email = request.form.get('email')
        result = User(user_name).check_password()
        if result:
            userrole = result['role']
            email_code = generate_randomint()
            password_new = hashlib.sha256(
                email_code.encode('utf-8')).hexdigest()
            User(user_name, password_new).update_password()

            msg_title = "Forget Password"
            sender = "noreply@app.com"
            msg = Message(msg_title, sender=sender, recipients=[
                          f'{email}'], body=f"Your new password is {email_code}")

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
    decorators = [login_required]
    # decorators = [catch_exception]

    def get(self):
        context = {}

        if g.userrole == 'student':
            context['student_info'] = session['student_info']
        elif g.userrole == 'staff':
            context['staff_info'] = session['staff_info']
        elif g.userrole == 'mentor':
            context['mentor_info'] = session['mentor_info']

        return render_template('/student/change_password.html', **context)

    def post(self):
        newpassword = request.form.get('newpassword')
        if newpassword:
            user_code = request.form.get('code')
            newpassword = hashlib.sha256(
                newpassword.encode('utf-8')).hexdigest()
            # print(session.get('who')['code'])
            if user_code == session.get('who')['code']:

                User(g.user_name, newpassword).update_password()
                session.pop('who')
                flash('Password has been changed successfully')
                return redirect(url_for('login'))
            else:
                flash('Wrong verification code, please enter again', 'red')
                return self.get()
        else:
            email = request.form.get('email')
            email_code = generate_randomint()
            session['who'] = {
                'email': email,
                'code': email_code
            }
            print(session.get('who'))
            sender = "noreply@app.com"
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

        base_path = os.path.dirname(os.path.abspath(__name__))
        str_path = r"/static/avatar/"
        upload_path = base_path + str_path + avatar.filename
        avatar.save(upload_path)
        database_path = "/static/avatar/" + avatar.filename
        session_path = "../static/avatar/" + avatar.filename

        User(g.user_name, database_path=database_path).update_avatar(
            g.user_name, database_path=database_path)
        session['Avatar_link'] = session_path
        url_link = request.referrer
        url_link = url_link.split('http://127.0.0.1:5000')[1]
        # print(url_link)
        flash('Your profile picture is updated')

        return redirect(f'{url_link}')


app.add_url_rule(
    '/update_avatar/', view_func=UpdateAvatar.as_view('update_avatar'))


class SendNotification(views.MethodView):
    decorators = [login_required]

    def get(self):
        form = NoticeForm()
        sql = '''select * from notification where send_to = %s order by receive_date Desc;'''
        para = (g.user_name,)
        results = run_data(sql, para, fetch=2)

        return render_template('/send_notice.html', form=form, results=results)

    def post(self):
        data = request.form.to_dict()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name_search = data['send_to']

        
        user_name_search = Notification(name=name_search).searchUsername(name=name_search)
        if not user_name_search:
            flash('The receiver does not exist, please enter again!','red')
            return self.get()
        else:
            user_name_search = user_name_search['user_name']

        # print(user_name_search)

        Notification(g.user_name, data=data, send_to=user_name_search, current_time=current_time).sentMail(
            g.user_name, data=data, send_to=user_name_search, current_time=current_time)

        flash('Message has been sent successfully')
        return self.get()


app.add_url_rule(
    '/send_notice/', view_func=SendNotification.as_view('send_notice'))


class NoticeControl(views.MethodView):
    decorators = [login_required]

    def get(self):
        # read = request.args.get('read')
        notice_id = request.args.get('notice_id')
        status = request.args.get('status')
        if status == 'unread':

            sql = '''update notification set status = "read" where notification_id = %s'''
            para = (notice_id,)
            run_data(sql, para)
            return redirect(url_for('send_notice'))
        else:

            return redirect(url_for('send_notice'))

    def post(self):

        data = request.form.to_dict()
        print(data)
        return 'ok'

app.add_url_rule(
    '/notice_control/', view_func=NoticeControl.as_view('notice_control'))


class SearchUser(views.MethodView):
    decorators = [login_required]

    def get(self):
        send_to_name = Notification().searchName()
        send_to_name = [name['name'] for name in send_to_name]
        # print(send_to_name)

        search_text = request.args.get('search', '')
        # # print(search_text)
        matching_names = [
            name for name in send_to_name if name.lower().startswith(search_text.lower())]

        if not matching_names:
            matching_names = ['No Match results']
        # print(matching_names)
        return jsonify({'names': matching_names})


app.add_url_rule(
    '/search_user/', view_func=SearchUser.as_view('search_user'))


@app.errorhandler(404)
def error_control(error):
    return render_template('404.html', title='404', error=error)


@app.route('/logout', methods=['POST', 'GET'])
@catch_exception
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
