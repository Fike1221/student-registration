from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from datetime import datetime
from functions import send_email, random_id, generate_salary, generate_grade


now = datetime.now()

# create instance of flask app
app = Flask(__name__)

# configure the mysql server env't
app.config["SECRET_KEY"] = "hey47fewod3i4rcmi3rurmxkp23od94jvxz../"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ''
app.config["MYSQL_DB"] = "registration_system"



@app.after_request
def add_cache_control_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



# initialize mysql server
mysql = MySQL(app)



@app.route('/')
@app.route('/dashboard')
def home():
    return render_template('home.html', head='Home')


@app.route('/student/register', methods=["POST", "GET"])
def register():
    try:
        if request.method == "POST":
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            email = request.form.get("email")
            phone_no = request.form.get("phone")
            dob = request.form.get("dob")
            department = request.form.get("department")
            password = request.form.get("pwd")
            confirm_pswd = request.form.get("cpwd")

            if password != confirm_pswd:
                flash("Your passwords are mismatched! Try again")
                return render_template('register.html', head="Register")
            

            
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * from student where stu_email=%s", (email, ))
            student_email = cursor.fetchone()

            if student_email:
                flash("You have already registered! Login here.")
                return redirect(url_for("login_student"))

            application_year = now.year
            student_id = f"mit/ur{random_id()}/{str(application_year)[2:]}"

            cursor.execute("SELECT * FROM department where dept_name=%s", (department, ))
            dept_info = cursor.fetchone()
            if not dept_info:
                flash("No such Dpeartment Available!")
                return render_template('register.html', head="Register") 

            dept_id = dept_info[0]
            no_of_stuedents = dept_info[2] + 1
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO student(student_id, stu_fname, stu_lname, stu_email, stu_phone, stu_dob, application_year, password, dept_id) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (student_id, fname, lname, email, phone_no, dob, application_year, hashed_password, dept_id))
            cursor.execute("UPDATE department SET n_students=%s where dept_id=%s", (no_of_stuedents, dept_id))
            mysql.connection.commit()
            cursor.close()
            send_email(email, f"Conguratulations!  {fname.title()} {lname.title()}  You have Successfully registered To MIT with ID number: {student_id}. Please keep Your ID If you forgote that you need to consult the registrar office. The Future is bright with MIT. Thank You!", "MIT registration")
            flash(f"Conguratulations {fname}! Now You are A memeber of our Campus. With ID: {student_id}")
            return redirect(url_for("login_student"))
    except Exception:
        flash("We are Sorry! Something went wrog. Please try refreshing the page.")

    return render_template('register.html', head="Register")


@app.route('/instructor/registration', methods=["POST", "GET"])
def instructor_registration():
    try:
        if request.method == "POST":
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            email = request.form.get("email")
            phone_no = request.form.get("phone")
            address = request.form.get("address")
            password = request.form.get("pwd")
            confirm_pswd = request.form.get("cpwd")

            if password != confirm_pswd:
                flash("Your passwords are mismatched! Try again")
                return render_template('instructor_registration.html', head="Instructor Registration")
            
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM instructor where ins_email=%s", (email, ))
            instructor_email = cursor.fetchone()

            if instructor_email:
                flash("You have already Applied! Login her as an instructor.")
                return redirect(url_for("login_instructor"))
            
            instructor_id = f"{fname.lower()}/{random_id()}"
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO instructor(instructor_id, instructor_fname, ins_email, ins_phone, instructor_lname, instructor_address, password) values(%s, %s, %s, %s, %s, %s, %s)", (instructor_id, fname, email, phone_no, lname, address, hashed_password))
            mysql.connection.commit()
            cursor.close()
            send_email(email, f"Conguratulations!  {fname.title()} {lname.title()}  You have Successfully Applied To MIT with ID number: {instructor_id}. Please keep Your ID If you forgote that you need to consult the registrar office. The Future is bright with MIT. Thank You!", "MIT Application")
            flash(f"You have Successfully Applied!  with ID: {instructor_id}")
            return redirect(url_for("login_instructor"))

    except Exception:
        flash("We are Sorry! Something went wrog. Please try refreshing the page.")

    return render_template("instructor_registration.html", head="Instructor Registration")


@app.route('/login/student', methods=["POST", "GET"])
def login_student():
    try:
        if request.method == "POST":
            student_id = request.form.get("studentId")
            password = request.form.get("password")

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM student where student_id=%s", (student_id, ))
            student_info = cursor.fetchone()
            cursor.close()

            if not student_info:
                flash("You have to register first!")
                return redirect(url_for("register"))
            
            
            id = student_info[0]
            full_name = f"{student_info[1]} {student_info[2]}"
            email = student_info[3]
            pswd = student_info[8]

            if student_id == id and check_password_hash(pwhash=pswd, password=password):
                session["student_id"] = student_id
                session["student_email"] = email
                session["student_name"] = student_info[1]
                flash(f"You have Successfully Logedin! {full_name}.")
                return redirect(url_for("student_profile"))
            
            else:
                flash("You have got wrong Password! Try again with correct password or Contact Registrar!")

    except Exception:
        flash("We are Sorry! Something went wrog. Please try refreshing the page.")

    return render_template('login_student.html', head="Student")


@app.route('/login/instructor', methods=["POST", "GET"])
def login_instructor():
    try:
        if request.method == "POST":
            id = request.form.get("instructorId")
            password = request.form.get("password")

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM instructor where instructor_id=%s", (id, ))
            instructor_info = cursor.fetchone()
            cursor.close()

            if not instructor_info:
                flash("You Are not an Employee yet! Need to Apply?")
                return redirect(url_for("instructor_registration"))
            
            instructor_id = instructor_info[0]
            instructor_email = instructor_info[2]
            full_name = f"{instructor_info[1]} {instructor_info[4]}"
            instructor_pswd = instructor_info[6]

            if instructor_id == id and check_password_hash(pwhash=instructor_pswd, password=password):
                session["instructor_id"] = instructor_id
                session["instructor_email"] = instructor_email
                session["instructor_name"] = instructor_info[1]
                flash(f"You have Successfully Logedin!  Ms. {full_name}")
                return redirect(url_for("instructor"))
            
            else:
                flash("You Have Got Incorrect Password!")

    except Exception:
        flash("We are Sorry! Something went wrog. Please try refreshing the page.")

    return render_template('login_instructor.html', head="Login")

@app.route('/student/profile')
def student_profile():

    if "student_id" in session:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM student WHERE student_id=%s", (session["student_id"], ))
            student_info = cursor.fetchone()
            current_year = now.year
            dept_id = student_info[9]
            cursor.execute("select dept_name from department where dept_id=%s", (dept_id, ))
            department = cursor.fetchone()
            cursor.execute("SELECT year, semester from enrollment where student_id=%s", (session["student_id"], ))
            enrollment_details = cursor.fetchall()
            cursor.close()
            department = department[0]
        except Exception:
            flash("We are sorry!  Something went please Try refreshing the page.")

        return render_template('student_profile.html', head="My Profile", details = student_info, department=department, year=enrollment_details, current_year=current_year)
    

    flash("You Have to login first to access this page!")

    return redirect(url_for("home"))

@app.route('/student/assessment/result')
def assessment_result():
    if "student_id" in session:
        try:
            current_year = now.year
            cursor = mysql.connection.cursor()
            cursor.execute("select distinct year, semester from enrollment where student_id=%s", (session["student_id"], ))
            year_and_semester = cursor.fetchone()
            cursor.execute("select course.course_id, course_title, credits, mark from course, enrollment where course.course_id=enrollment.course_id and student_id=%s", (session["student_id"], ))
            assessment_info = cursor.fetchall()

            my_dict = {}
            for assessment in assessment_info:
                my_dict[assessment[0]] = [assessment[2], assessment[3]]
            total_credit = 0
            grades = []
            total_points = 0.0
            total_mark = 0
            for key in my_dict:
                total_credit += my_dict[key][0]
                grades.append(generate_grade(my_dict[key][1])[0])
                total_points += (generate_grade(my_dict[key][1])[1] * my_dict[key][0])
                total_mark += my_dict[key][1]

            semester_gpa = total_points/total_credit
            for key in my_dict:
                if my_dict[key][1] == 0.0:
                    semester_gpa = 0.0
                    break
            cursor.execute("UPDATE student SET GPA=%s WHERE student_id=%s", (semester_gpa, session["student_id"]))
            mysql.connection.commit()
            cursor.close()

        except Exception:
            flash("We are sorry!  Something went please Try refreshing the page.")
        return render_template('assessment_result.html', head="Assessment Result", academic_year=current_year, year_and_semester=year_and_semester, assessments=assessment_info, GPA=semester_gpa, grades=grades, total_credit=total_credit, total_mark=total_mark)

    flash("You are not Autherized to access this page.  You have to login first!")
    return redirect(url_for("home"))


@app.route('/student/enrollment', methods=["POST", "GET"])
def student_enrollment():
    if "student_id" in session:
        try:
            valid_semester = 1 if now.month <=6 else valid_semester == 2
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM student WHERE student_id=%s", (session["student_id"], ))
            student_info = cursor.fetchone()
            cursor.close()
            registraion_year = student_info[7]
            dept_id = student_info[9]
            valid_year = now.year - registraion_year + 1


            if request.method == "POST":
                year = request.form.get("year")
                semester = request.form.get("semester")

                cursor = mysql.connection.cursor()
                cursor.execute("SELECT * FROM enrollment where student_id=%s and year=%s and semester=%s", (session["student_id"], year, semester))
                enrollment_info = cursor.fetchone()
                
                if enrollment_info:
                    flash("You have Already Enrolled!")

                else:
                    cursor.execute("SELECT course_id FROM offers where dept_id=%s", (dept_id, ))
                    course_info = cursor.fetchall()
                    cursor.execute("INSERT INTO enrollment(year, semester, dept_id, course_id, student_id) values(%s, %s, %s, %s, %s)", (year, semester, dept_id, course_info[0][0], session["student_id"]))
                    cursor.execute("INSERT INTO enrollment(year, semester, dept_id, course_id, student_id) values(%s, %s, %s, %s, %s)", (year, semester, dept_id, course_info[1][0], session["student_id"]))
                    cursor.execute("INSERT INTO enrollment(year, semester, dept_id, course_id, student_id) values(%s, %s, %s, %s, %s)", (year, semester, dept_id, course_info[2][0], session["student_id"]))
                    mysql.connection.commit()
                    cursor.close()
                    flash("You have Successfully Enrolled! for This Semester")        
       
        except Exception:
            flash("We are sorry!  Something went please Try refreshing the page.")

        return render_template('enrollment.html', head="Enrollment", semester=valid_semester, valid_year=valid_year)
    
    flash("You are not Autherized to access this page!  please login first")
    return redirect(url_for("home"))



@app.route('/student/support/center', methods=["POST", "GET"])
def support():
    if "student_id" in session:
        try:
            if request.method == "POST":
                content = request.form.get("issue")
                send_email(session["student_email"], content, "Support From Student")
                flash("Received!")

        except Exception:
            flash("We are Sorry! Something went wrog. Please try refreshing the page.")

        return render_template('support.html', head="Student Support Center")
    
    flash("You Are not authorized to access this page!")
    return redirect(url_for("home"))



@app.route('/instructor/profile')
def instructor():
    if "instructor_id" in session:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM instructor WHERE instructor_id=%s", (session["instructor_id"], ))
            instructor_info = cursor.fetchone()
            cursor.close()
        except Exception:
            flash("We are Sorry! Something went wrog. Please try refreshing the page.")

        return render_template('instructor_profile.html', head="Instructor", details=instructor_info)
    
    else:
        flash("You Are Not Authorized to access this page!")
        return redirect(url_for("home"))


@app.route('/instructor/enroll/courses', methods=["POST", "GET"])
def courses():
    if "instructor_id" in session:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT course_title FROM course")
            course_titles = cursor.fetchall()
            cursor.close()
            salary = float(generate_salary())
            if request.method == "POST":
                course = request.form.get("Courses")

                cursor = mysql.connection.cursor()
                cursor.execute("SELECT * FROM course where instructor_id=%s", (session["instructor_id"], ))
                course_info = cursor.fetchall()
                cursor.close()

                if len(course_info) > 1:
                    flash("You can't instruct more than Two courses!")
                    
                else:
                    cursor = mysql.connection.cursor()
                    cursor.execute("SELECT * FROM course where course_title=%s", (course, ))
                    course_data = cursor.fetchone()

                    if course_data[3]:
                        flash(f"{course} has been taken by someone already. Try another one.")

                    else:
                        cursor.execute("UPDATE course SET instructor_id=%s WHERE course_title=%s", (session["instructor_id"], course))
                        cursor.execute("UPDATE instructor SET salary=%s WHERE instructor_id=%s", (salary, session["instructor_id"]))
                        mysql.connection.commit()
                        cursor.close()
                        flash(f"You have successfully Added:  {course}!")
        except Exception:
            flash("We are Sorry! Something went wrog. Please try refreshing the page.")

        return render_template("courses.html", head="Register in Courses", course_names = course_titles)

    flash("You Are Not Authorized to access this page!")
    return redirect(url_for("home"))



@app.route('/instructor/course/audit', methods=["POST", "GET"])
def course_audit():
    if "instructor_id" in session:
        try:
            students1 = None
            students2 = None
            course1 = None
            course2 = None
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM course WHERE instructor_id=%s", (session["instructor_id"], ))
            course_info = cursor.fetchall()
            if not course_info:
                flash("You Haven't Enrolled yet!")
            else:
                if len(course_info) == 1:
                    course1 = course_info[0]
                    cursor.execute("select student.student_id, stu_fname, stu_lname, student.dept_id from student, enrollment where enrollment.student_id = student.student_id and enrollment.course_id=%s", (course1[0], ))
                    students1 = cursor.fetchall()
                

                if len(course_info) == 2:
                    course1 = course_info[0]
                    cursor.execute("select student.student_id, stu_fname, stu_lname, student.dept_id from student, enrollment where enrollment.student_id = student.student_id and enrollment.course_id=%s", (course1[0], ))
                    students1 = cursor.fetchall()
                    course2 = course_info[1]
                    cursor.execute("select student.student_id, stu_fname, stu_lname, student.dept_id from student, enrollment where enrollment.student_id = student.student_id and enrollment.course_id=%s", (course2[0], ))
                    students2 = cursor.fetchall()
                    cursor.close()

            if request.method == "POST":
                submitted_course = request.form.get("form_type")
                if submitted_course == "course1":
                    for student in students1:
                        mark = request.form.get(f"{student[0]}")
                        mark = float(mark)
                        cursor = mysql.connection.cursor()
                        cursor.execute("UPDATE enrollment SET mark=%s WHERE course_id=%s and student_id=%s", (mark, course1[0], student[0]))
                        mysql.connection.commit()
                        cursor.close()

                elif submitted_course == "course2":
                    for student in students2:
                        mark = request.form.get(f"{student[0]}")
                        mark = float(mark)
                        cursor = mysql.connection.cursor()
                        cursor.execute("UPDATE enrollment SET mark=%s WHERE course_id=%s and student_id=%s", (mark, course2[0], student[0]))
                        mysql.connection.commit()
                        cursor.close()
        except Exception:
            flash("We are Sorry! Something went wrog. Please try refreshing the page.")

        return render_template('course_audit.html', head="Course Audit", course1 = course1, course2=course2, students1=students1, students2=students2)
    
    flash("You Are Not Authorized to access this page!")
    return redirect(url_for("home"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
