from app import app
from flask import render_template, request, redirect
import users
import courses
import exercises
import materials

@app.route("/enroll/<int:course_id>", methods=["GET", "POST"])
def enroll(course_id):
    course = courses.get_course(course_id)
    if not course:
        return render_template("error.html", message="Kurssia ei löytynyt.")

    if request.method == "GET":
        return render_template("enroll.html", course_id=course_id, course_name=course[1])

    if request.method == "POST":
        users.check_csrf()
        student_id = users.get_user_id()
        error_messages = []
        user_role = users.get_user_role()

        if user_role != "student":
            error_messages.append("Vain opiskelijat voivat ilmoittautua kursseille.")

        if not users.has_userinfo():
            error_messages.append("Täydennä ensin käyttäjätietosi!")

        if courses.check_if_student_is_enrolled(course_id, student_id):
            error_messages.append("Olet jo ilmoittautunut kurssille!")

        if len(error_messages) == 0:
            if courses.enroll_on_course(course_id, student_id):
                return redirect("/course_page/" + str(course_id))
            return render_template("error.html", message="Ilmoittautuminen epäonnistui.")

        return render_template("error.html", error_messages=error_messages)

@app.route("/course_page/<int:course_id>")
def show_coursepage(course_id):
    course = courses.get_course(course_id)
    if course:
        course_name = course[1]
        description = course[2]
        teacher = course[4] + ' ' + course[5]
        enrolled = False
        owner = False
        course_exercises = exercises.get_exercises(course_id)
        exercise_answers = []
        course_materials = materials.get_course_materials(course_id)
        user_id = users.get_user_id()
        points = 0

        if user_id != 0:
            owner = courses.check_if_owner(user_id, course_id)
            if owner:
                exercise_answers = exercises.get_all_course_exercise_answers(course_id)

            enrolled = courses.check_if_student_is_enrolled(course_id, user_id)
            if enrolled:
                exercise_answers = exercises.get_students_course_exercise_answers(user_id, course_id)
                points = exercises.get_correct_answers(user_id, course_id)

        return render_template("course_page.html", id=course_id,
                                                course_name=course_name,
                                                description=description,
                                                teacher=teacher,
                                                enrolled=enrolled,
                                                owner=owner,
                                                exercise_list=course_exercises,
                                                answers=exercise_answers,
                                                points = points,
                                                materials=course_materials)

    return render_template("error.html", message="Kurssitietoja ei löytynyt.")

@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    if users.get_user_role() != "teacher":
        return render_template("error.html", message="Vain opettajat voivat lisätä kursseja!")

    if request.method == "GET":
        if not users.has_userinfo():
            return render_template("error.html", message="Täydennä ensin käyttäjätietosi!")
        return render_template("add_course.html")

    if request.method == "POST":
        users.check_csrf()
        course_name = request.form["course_name"]
        description = request.form["description"]
        user_id = users.get_user_id()
        error_messages = []

        if len(course_name) < 3 or len(course_name) > 100:
            error_messages.append("Kurssin nimen on oltava 3-100 merkkiä.")
        if len(description) < 1 or len(description) > 2000:
            error_messages.append("Kurssikuvauksen on oltava 1-2000 merkkiä.")

        if len(error_messages) == 0:
            if courses.add_course(user_id, course_name, description):
                return redirect("/homepage")
            return render_template("error.html", message="Kurssin lisäys ei onnistunut.")

        return render_template("add_course.html", error_messages=error_messages,
                                                  name=course_name,
                                                  description=description)

@app.route("/update_course/<int:course_id>", methods=["GET", "POST"])
def update_course(course_id):
    user_id = users.get_user_id()
    if not courses.check_if_owner(user_id, course_id):
        return render_template("error.html", message="Vain kurssin opettaja voi muokata kurssitietoja!")

    if request.method == "GET":
        course = courses.get_course(course_id)
        if course:
            course_name = course[1]
            description = course[2]
            return render_template("update_course.html", course_id=course_id,
                                                         course_name=course_name,
                                                         description=description)

        return render_template("error.html", message="Kurssia ei löytynyt tietokannasta")

    if request.method == "POST":
        users.check_csrf()
        course_name = request.form["course_name"]
        description = request.form["description"]
        error_messages = []

        if len(course_name) < 3 or len(course_name) > 100:
            error_messages.append("Kurssin nimen on oltava vähintään 3-100 merkkiä.")
        if len(description) < 1 or len(description) > 2000:
            error_messages.append("Kurssikuvauksen on oltava 1-2000 merkkiä.")

        if len(error_messages) == 0:
            if courses.update_course(user_id, course_id, course_name, description):
                return redirect("/course_page/" + str(course_id))
            return render_template("error.html", message="Kurssin päivitys ei onnistunut.")

        return render_template("update_course.html", error_messages=error_messages,
                                                     course_id=course_id,
                                                     course_name=course_name,
                                                     description=description)

@app.route("/delete_course/<int:course_id>")
def delete_course(course_id):
    user_id = users.get_user_id()
    if not courses.check_if_owner(user_id, course_id):
        return render_template("error.html", message="Vain kurssin opettaja voi poistaa kurssin!")

    if courses.delete_course(user_id, course_id):
        return redirect("/homepage")

    return render_template("error.html", message="Kurssin poistaminen ei onnistunut.")
