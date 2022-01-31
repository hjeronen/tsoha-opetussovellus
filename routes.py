from app import app
from flask import render_template, request, redirect
import login_service
import courses

@app.route("/")
def index():
    all_courses = courses.get_all_courses()
    return render_template("index.html", list = all_courses)

@app.route("/homepage")
def homepage():
    # if not login_service.check_csrf():
    #     return render_template("error.html")
    user_id = login_service.get_userID()
    users_courses = courses.get_users_courses(user_id, login_service.get_user_role())
    return render_template("homepage.html", list=users_courses)

@app.route("/enroll/<int:course_id>")
def enroll(course_id):
    user_role = login_service.get_user_role()
    student_id = login_service.get_userID()
    if not login_service.has_userinfo():
        return "Täydennä ensin käyttäjätietosi!"
    if courses.check_if_student_is_enrolled(course_id, student_id):
        return render_template("error.html")
    if courses.enroll_on_course(course_id, student_id, user_role):
        return render_template("success.html")
    else:
        return render_template("error.html")

@app.route("/course_page/<int:course_id>")
def show_coursepage(course_id):
    info = courses.get_course(course_id)
    if info:
        id = info[0]
        course_name = info[1]
        description = info[2]
        teacher_id = info[3]
        teacher = info[4] + ' ' + info[5]
        enrolled = False
        owner = False
        if login_service.has_userinfo():
            user_id = login_service.get_userID()
            if teacher_id == user_id:
                owner = True
            if login_service.get_user_role() == 'student':
                enrolled = courses.check_if_student_is_enrolled(course_id, user_id)
        return render_template("course_page.html", id = course_id, course_name = course_name, description = description, teacher=teacher, enrolled=enrolled, owner=owner)
    else:
        return render_template("error.html")

@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    if request.method == "GET":
        if not login_service.has_userinfo():
            return "Täytä ensin käyttäjätietosi!"
        return render_template("add_course.html")
    if request.method == "POST":
        course_name = request.form["course_name"]
        description = request.form["description"]
        user_id = login_service.get_userID()
        user_role = login_service.get_user_role()
        if courses.add_course(user_id, user_role, course_name, description):
            return render_template("success.html")
        else:
            return render_template("error.html")

@app.route("/update_course/<int:course_id>", methods=["GET", "POST"])
def update_course(course_id):
    if request.method == "GET":
        info = courses.get_course(course_id)
        if info:
            course_name = info[1]
            description = info[2]
            return render_template("update_course.html", course_id = course_id, course_name = course_name, description = description)
        else:
            return render_template("error.html")
    if request.method == "POST":
        course_name = request.form["course_name"]
        description = request.form["description"]
        user_id = login_service.get_userID()
        user_role = login_service.get_user_role()
        if courses.update_course(user_id, user_role, course_id, course_name, description):
            return render_template("success.html")
        else:
            return render_template("error.html")

@app.route("/delete_course/<int:course_id>")
def delete_course(course_id):
    user_id = login_service.get_userID()
    user_role = login_service.get_user_role()
    if courses.delete_course(user_id, user_role, course_id):
        return render_template("success.html")
    else:
        return render_template("error.html")

@app.route("/userinfo", methods=["GET", "POST"])
def user_info():
    if request.method == "GET":
        if login_service.get_userID():
            info = login_service.get_userinfo()
            if info:
                return render_template("show_userinfo.html", list=info)
            else:
                return render_template("userinfo.html")
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        student_number = 0
        if login_service.get_user_role() == 'student':
            student_number = request.form["student_number"]
        if login_service.save_user_info(firstname, lastname, student_number):
            return render_template("success.html")
        else:
            return render_template("error.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        if login_service.register(username, password, role):
            return render_template("success.html")
        else:
            return render_template("error.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if login_service.login(username, password):
            return render_template("success.html")
        else:
            return render_template("error.html")
    
@app.route("/logout")
def logout():
    if login_service.logout():
        return render_template("success.html")
    else:
        return render_template("error.html")
    
@app.route("/delete_account")
def delete_account():
    if login_service.delete_account():
        return render_template("success.html")
    else:
        return render_template("error.html")