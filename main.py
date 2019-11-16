
#=========================================================================
#LIBRARIES IMPORT
import os
from flask import Flask, render_template, request, flash, url_for, redirect, sessions, session
from flask_mysqldb import MySQL
import random
from datetime import date
import xlrd
import pyodbc
import sms
from werkzeug.utils import secure_filename
from passlib.hash import pbkdf2_sha256

#==========================================================================
#GLOBAL VARIABLES

otp1 = 'none'
studentTableName = 'studentlogininfo'
facultyTableName = 'facultylogininfo'

#==========================================================================
#APPLICATION INIT.

app = Flask(__name__)

#=============================================================================
#MYSQL CONFIGURATION
app.config['SECRET_KEY'] = 'AjJ0lXaX5K9tai8QsUhwwQ'
server = 'anant.database.windows.net'
database = 'collegeplus'
username = 'root7'
password = 'Anant@1707'
driver= 'ODBC Driver 17 for SQL Server'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

#===============================================================================



#HOMEPAGE

@app.route('/')
def home():
    if(session.get('username')):
        session.pop('username',None)
    return render_template('index.html',title='Home')

#================================================================================
#LOGIN & REGISTER

@app.route('/register', methods=['GET', 'POST'])
def register():
    cur = cnxn.cursor()
    if request.method == 'POST':
        logininfo = request.form
        fname = logininfo['fname']
        lname = logininfo['lname']
        email = logininfo['email']
        sid = logininfo['sid']
        phone = logininfo['phone']
        password = logininfo['password']
        confirmpassword = logininfo['confirmpass']
        stream = logininfo['stream']

        values = (fname, lname, sid, email, pbkdf2_sha256.hash(password), phone,stream)
        if (password == confirmpassword):
            try:
                cur.execute(f"INSERT INTO " + studentTableName + " VALUES" + f"{values}")
            except:
                flash("Account already exists",'info')
                return redirect(url_for('studentlogin'))
            else:

                cur.commit()
            cnxn.close()
            flash("Thanks for Registering", 'success')
            return redirect(url_for('home'))
        else:
            flash("Password didnt match", 'danger')
            return redirect(url_for('register'))

    return render_template('register.html',title="Register")


@app.route('/studentlogin', methods=['GET', 'POST'])
def studentlogin():
    if (session.get('username')):
        session.pop('username', None)
    cur = cnxn.cursor()
    if request.method == 'POST':
        slogininfo = request.form
        ssid = slogininfo['sid']
        password = slogininfo['password']
        cur.execute(f"SELECT passwordd FROM {studentTableName} where sid = '{ssid}'")
        a=cur.fetchone()
        if(a == None):
            flash("You are not registered!!,REGISTER NOW", 'danger')
            return redirect(url_for('register'))
        else:
            cur.execute(f"SELECT passwordd FROM {studentTableName} where sid = '{ssid}'")
            if (pbkdf2_sha256.verify(password,a[0])):

                session['logged_in'] = True
                session['username'] = ssid
                cur.execute(f"SELECT fname FROM {studentTableName} where sid = '{ssid}'")
                fname = cur.fetchone()

                flash(f'welcome {fname[0]}', 'success')

                cnxn.close()
                return redirect(url_for('studentloggedin'))
            else:
                flash("WRONG PASSWORD", 'danger')
                cnxn.close()
                return redirect(url_for('studentlogin'))

    return render_template("student-login.html",title="Login")


@app.route('/facultylogin', methods=['GET', 'POST'])
def facultylogin():
    if (session.get('username')):
        session.pop('username', None)

    cur = cnxn.cursor()
    if request.method == 'POST':
        flogininfo = request.form
        username = flogininfo['logid']

        password = flogininfo['password']

        cur.execute(f"select passwordd from {facultyTableName} where loginid= '{username}'")
        a=cur.fetchone()
        if(a == None):
            flash("Only Faculty can Login. Contact admin if you think this is a mistake.",'danger')
            return redirect(url_for('home'))

        if password == a[0]:
            cur.execute(f"select loginid from facultylogininfo")
            session['log-in'] = True
            session['username']=username

            return redirect(url_for('facultyloggedin'))
        else:
            flash('Invalid Username or Password', 'danger')
            return redirect(url_for('facultylogin'))
    return render_template('faculty-login.html',title="Login")


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    global otp1
    cur = cnxn.cursor()
    if request.method == 'POST':
        slogininfo = request.form
        ssid = slogininfo['sid']
        cur.execute(f"select phone from studentlogininfo where sid = '{ssid}' ")
        a=cur.fetchone()
        if(a == None):
            flash("You are not registered!!,REGISTER NOW", 'danger')
            return redirect(url_for('register'))
        else:
            otp1 = str(random.randrange(100000, 999999))
            URL = 'https://www.way2sms.com/api/v1/sendCampaign'
            cur.execute(f"SELECT phone FROM {studentTableName} where sid= {ssid}")
            print(otp1)
            #sms.sendPostRequest(URL, 'C23FTIDPYUYZVP7UV238S0QC1POBFWMR', 'N1AY9Q2S52NHUADE', 'stage', a[0], '9781396442', f"Your OTP (One Time Password) to change your password is: {otp1} Do not share this with anyone!   Team college+")
            return redirect(url_for('resetpass', phonenumber=a[0]))

    return render_template('forgot.html',title="Forgot Password")


@app.route('/reset<phonenumber>', methods=['GET', 'POST'])
def resetpass(phonenumber):
    cur = cnxn.cursor()
    print(otp1)
    if request.method == 'POST':
        slogininfo = request.form
        ootp = slogininfo['otp']


        if ootp == (otp1):
            return redirect(url_for('newpass', phonenumber2=phonenumber))
        else:
            flash('INVALID OTP', 'danger')
            return redirect(url_for('resetpass', phonenumber=phonenumber))

    return render_template('otpverify.html',title="Verify")


@app.route('/newpass<phonenumber2>', methods=['GET', 'POST'])
def newpass(phonenumber2):
    cur = cnxn.cursor()
    if request.method == 'POST':
        slogininfo = request.form
        newpassword = slogininfo['password']
        confirmnewpassword = slogininfo['cpassword']

        if (newpassword == confirmnewpassword):
            newpassworda=pbkdf2_sha256.hash(newpassword)

            

            cur.execute(f" UPDATE  {studentTableName}  set passwordd = '{newpassworda}' where phone =  '{phonenumber2}' ")
            cur.commit()
            return redirect(url_for('studentlogin'))
        else:
            flash("passwords didnt match", 'danger')
            return redirect(url_for('newpass', phonenumber2=phonenumber2))
    return render_template('newpass.html',title="New Password")


@app.route('/changepass',methods=['GET','POST'])
def changepass():
    cur = cnxn.cursor()
    if request.method == 'POST':
        slogininfo = request.form
        cur.execute(f"select passwordd from studentlogininfo where sid = {session['username']}")
        currentpass=slogininfo['currentpass']
        currentpassword = cur.fetchone()[0]
        newpassword = slogininfo['password']
        confirmnewpassword = slogininfo['cpassword']
        if(pbkdf2_sha256.verify(currentpass,currentpassword)):

            if (newpassword == confirmnewpassword):
                newpassworda=pbkdf2_sha256.hash(newpassword)

                query = f" UPDATE  {studentTableName}  set passwordd = '{newpassworda}' where sid = '{session['username']}' "

                cur.execute(query)
                cur.commit()
                return redirect(url_for('studentlogin'))
            else:
                flash("passwords didnt match", 'danger')
                return redirect(url_for('changepass'))
        else:
            flash("Enter Correct Current Password",'warning')
            return redirect(url_for('changepass'))


    return render_template('changepass.html',title="Change Password")

@app.route('/changepassf',methods=['GET','POST'])
def changepassf():
    cur = cnxn.cursor()
    if request.method == 'POST':
        flogininfo = request.form
        cur.execute(f"select passwordd from facultylogininfo where loginid = '{session['username']}'")
        currentpass=flogininfo['currentpass']
        currentpassword = cur.fetchone()[0]
        newpassword = flogininfo['password']
        confirmnewpassword = flogininfo['cpassword']
        if(currentpass == currentpassword):

            if (newpassword == confirmnewpassword):

                query = f" UPDATE  {facultyTableName}  set passwordd = '{newpassword}' where loginid = '{session['username']}' "

                cur.execute(query)
                cur.commit()
                return redirect(url_for('facultylogin'))
            else:
                flash("passwords didnt match", 'danger')
                return redirect(url_for('changepass'))
        else:
            flash("Enter Correct Current Password",'warning')
            return redirect(url_for('changepassf'))


    return render_template('changepassf.html',title="Change Password")

#====================================================================================
#STUDENT HOME
@app.route('/studentloggedin')
def studentloggedin():

    if (session.get('username')):
        cur = cnxn.cursor()
        cur.execute(f"select stream from studentlogininfo where sid='{session['username']}'")
        a = cur.fetchone()
        strin = a[0]
        cur.execute (f'''SELECT f.fname,f.lname , a.postdate,a.title,a.content
        FROM announcements a 
        JOIN facultylogininfo f 
        ON a.author=f.loginid 
        WHERE receivers='{strin}' 
        ORDER BY a.postdate desc ,a.priority ''')

        a = cur.fetchall()
        ssid = session.get('username')
        cur.execute(f"select * from studentlogininfo where sid={ssid}")
        b = cur.fetchone()
        name = b[0] + " " + b[1]

        email = b[3]
        phonenumber = b[5]

        return render_template('studenthome.html',title="Dashboard" ,tasks=a,name=name, email=email,ssid=ssid, phonenumber=phonenumber)

    else:
        flash('You are not Logged-In!','info')
        return redirect(url_for('studentlogin'))


@app.route('/coursemanager')
def coursemanager():
    if (session.get('username')):
        cur = cnxn.cursor()
        cur.execute("select subid from subjectlist")
        courses = cur.fetchall()
        subjects = []
        for i in range(len(courses)):
            cur.execute(
                f"select f.fname,f.lname from facultylogininfo f JOIN subjectlist s on s.instructorid=f.loginid where subid = '{courses[i][0]}'")
            names = cur.fetchone()
            subjects.append((courses[i][0], names[0] + " " + names[1]))

        return render_template('coursemanager.html', title="Manager",subjects=subjects)
    else:
        flash('You are not Logged-In!', 'info')
        return redirect(url_for('studentlogin'))


@app.route('/course<courseid>')
def course(courseid):
    if(session.get('username')):
        cur=cnxn.cursor()
        cur.execute("select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='marklist'")
        a=cur.fetchall()
        cur.execute(f"select * from marklist where subid = '{courseid}' and sid = '{session['username']}'")
        b=cur.fetchall()
        cur.execute(f"select l,t,p from subjectlist where subid = '{courseid}'")
        ltp=cur.fetchone()
        ltpvalues=('lecture','tutorial','practical')
        attendance=[]
        for i in range(3):
            if(ltp[i]==0):
                pass
            else:
                cur.execute(f"select * from attendance{ltpvalues[i][0]} where sid = '{session['username']}' and subid = '{courseid}'")
                x=cur.fetchone()
                x=list(x)
                x.append(ltpvalues[i])
                attendance.append(x)

        return render_template('course.html',title=f"Course-{courseid}",a=a,b=b,attendance=attendance)
    else:
        flash('You are not Logged-In','info')
        return redirect(url_for('facultylogin'))

@app.route('/sharedmaterial')
def sharedmaterial():
    if (session.get('username')):
        cur = cnxn.cursor()
        cur.execute(f"select stream from studentlogininfo where sid='{session['username']}'")
        a = cur.fetchone()
        strin = a[0]
        cur.execute (f'''SELECT f.fname,f.lname , fl.posttdate,fl.title,fl.descriptions,fl.filename,fl.fext
        FROM files fl 
        JOIN facultylogininfo f 
        ON fl.author=f.loginid
        WHERE fl.recievers='{strin}' 
        ORDER BY fl.posttdate desc  ''')
        dir = os.getcwd()

        a = cur.fetchall()
        return render_template('sharedmaterial.html',title="Shared Material" ,tasks=a)
    else:
        flash('You are not Logged-In!','info')
        return redirect(url_for('studentlogin'))

#====================================================================================
#FACULTY HOME
@app.route('/facultyloggedin', methods=['GET', 'POST'])
def facultyloggedin():
    if(session.get('username')):
        cur = cnxn.cursor()
        cur.execute(f"select department from facultylogininfo where loginid='{session['username']}'")
        a = cur.fetchone()
        department = a[0]
        cur.execute(f"select DISTINCT f.fname, f.lname , a.postdate , a.title , a.content, a.ano from announcements a join facultylogininfo f on a.author = f.loginid where f.loginid = '{session['username']}'")
        a  = cur.fetchall()

        loginid=session['username']
        cur.execute(f"select * from facultylogininfo where loginid= '{loginid}'")
        b = cur.fetchone()
        name = b[0] + " " + b[1]

        email = b[3]
        phonenumber = b[6]

        return render_template('facultyhome.html',title="Dashboard", tasks=a, name=name, email=email, department=department, phonenumber=phonenumber)
    else:
        flash('You are not Logged-In','info')
        return redirect(url_for('facultylogin'))


@app.route('/facultyannouncement', methods=['GET', 'POST'])
def facultyannouncement():
    if(session.get('username')):
        cur=cnxn.cursor()

        if request.method == 'POST':
            cur.execute(f"select max(ano) from announcements")
            abc=cur.fetchone()[0]

            if (abc == None):
                ano = 0
            else:
                ano = int(abc)

            ano += 1
            info = request.form
            loginid=session['username']
            today=date.today()
            title=info['title']
            content=info['content']
            priority=info['priority']
            for i in info.getlist('stream'):
                receivers=i
                values=f"('{loginid}','{content}','{today}','{receivers}','{title}','{priority}','{ano}')"
                cur.execute(f"INSERT into announcements values{values}")
            cur.commit()
            flash('announcement successfully added','success')
            return redirect(url_for('facultyloggedin'))

        return render_template("facultyannouncement.html",title="Upload Announcement")

    else:
        flash('You are not Logged-In','info')
        return redirect(url_for('facultylogin'))


@app.route('/delete<ano>')
def delete(ano):
    if(session.get('username')):
        cur=cnxn.cursor()
        cur.execute(f"DELETE FROM ANNOUNCEMENTS WHERE ano = '{ano}'")
        cur.commit()
        return redirect(url_for('facultyloggedin'))
    else:
        flash('You are not Logged-In','info')
        return redirect(url_for('facultylogin'))


@app.route('/edit<ano>',methods=["GET","POST"])
def edit (ano):
    if(session.get('username')):
        cur=cnxn.cursor()
        if request.method == 'POST':
            info=request.form
            content=info['content']
            title=info['title']
            cur.execute(f" update  announcements set title='{title}',content='{content}' where ano={ano} ")
            cur.commit()
            return redirect(url_for('facultyloggedin'))

        cur.execute(f"SELECT * FROM ANNOUNCEMENTS WHERE ano= {ano}")
        a=cur.fetchone()
        return render_template('update.html',task=a,title="Edit")
    else:
        flash('You are not Logged-In','info')
        return redirect(url_for('facultylogin'))


@app.route('/addresult',methods=['GET','POST'])
def addresult():
    if(session.get('username')):
        cur = cnxn.cursor()
        if request.method == 'POST':
            data=request.form
            subject=data['subject']
            file=request.files['markscsv']
            if not os.path.exists(os.getcwd() + '\\static\\results'):
                os.makedirs(os.getcwd() + '\\static\\results')
            file.save(os.getcwd() + '\\static\\results\\' + secure_filename(file.filename))
            book=xlrd.open_workbook(os.getcwd() + '\\static\\results\\'+f'{file.filename}')
            sheet=book.sheet_by_index(0)
            for r in range(1, sheet.nrows):
                sid = sheet.cell(r, 0).value
                mst = sheet.cell(r, 1).value
                mstt = sheet.cell(r, 2).value
                est = sheet.cell(r, 3).value
                estt = sheet.cell(r, 4).value
                project = sheet.cell(r, 5).value
                projectt= sheet.cell(r, 6).value
                quiz = sheet.cell(r, 7).value
                quizt= sheet.cell(r, 8).value
                sid=str(sid)
                sid=sid[0:8]
                cur.execute(f"delete from marklist where subid = '{subject}'")
                cur.execute(F"INSERT INTO MARKLIST VALUES ('{subject}','{sid}','{mst}','{mstt}','{est}','{estt}','{project}','{projectt}','{quiz}','{quizt}')")
                cur.commit()
            flash('Result added successfully','success')
            return redirect(url_for('facultyloggedin'))
        cur.execute("select subid from subjectlist")
        a = cur.fetchall()
        return render_template('addresult.html', a=a,title="Upload Result")
    else:
        flash('You are not Logged-In','info')
        return redirect(url_for('facultylogin'))


@app.route('/attendanceupload',methods=['GET','POST'])
def attendanceupload():
    if(session.get('username')):
        cur = cnxn.cursor()
        if request.method == 'POST':
            data=request.form
            subid=data['subject']
            file=request.files['attendance']
            if not os.path.exists(os.getcwd() + '\\static\\attendance'):
                os.makedirs(os.getcwd() + '\\static\\attendance')
            file.save(os.getcwd() + '\\static\\attendance\\' + secure_filename(file.filename))

            book=xlrd.open_workbook(os.getcwd()+'\\static\\attendance\\'+f'{file.filename}')
            cur.execute(f"select l,t,p from subjectlist where subid = '{subid}' ")
            a=cur.fetchone()
            ltpvalues=['l','t','p']
            for i in range(3):
                if (a[i] == 0):
                    pass
                else:
                    cur.execute(f"delete from attendance{ltpvalues[i]} where subid='{subid}'")
                    sheet = book.sheet_by_index(i)
                    for r in range(1, sheet.nrows):
                        sid = sheet.cell(r, 0).value
                        attended = sheet.cell(r, 1).value
                        total = sheet.cell(r, 2).value
                        sid = str(sid)
                        sid = sid[0:8]
                        cur.execute(f"INSERT INTO attendance{ltpvalues[i]} VALUES('{subid}','{sid}','{attended}','{total}')")
                        cur.commit()
            flash('Attendance uploaded successfully','success')
            return redirect(url_for('facultyloggedin'))
        cur.execute("select subid from subjectlist")
        a = cur.fetchall()
        return render_template('attendanceupload.html', a=a,title="Update Attendance")
    else:
        flask('You are not Logged-In','info')
        return redirect(url_for('facultylogin'))

@app.route('/uploadfile',methods=['GET',"POST"])
def uploadfile():
    if (session.get('username')):
        cur = cnxn.cursor()

        if request.method == 'POST':
            cur.execute(f"select max(fno) from files")
            abc = cur.fetchone()[0]
            

            if (abc == None):

                fno = 0
            else:

                fno = int(abc)

            fno = fno+1
            info = request.form

            file = request.files['file']
            if not os.path.exists(os.getcwd() + '\\static\\studymaterial'):
                os.makedirs(os.getcwd() + '\\static\\studymaterial')
            fname, fext = os.path.splitext(file.filename)



            cur.execute(f"select subid from subjectlist where instructorid ='{session['username']}'")
            subid=cur.fetchone()[0]
            today = date.today()
            title = info['title']
            descriptions = info['description']

            for i in info.getlist('stream'):
                receivers = i
                values = f"('{subid}','{title}','{descriptions}','{today}','{receivers}','{fname}','{fno}','{fext}','{session['username']}')"
                file.save(os.getcwd() + '\\static\\studymaterial\\' + secure_filename(file.filename))
                cur.execute(f"INSERT into files values{values}")
            cur.commit()
            flash('File successfully uploaded', 'success')
            return redirect(url_for('facultyloggedin'))

        return render_template("uploadfile.html",title="Add Material")

    else:
        flash('You are not Logged-In', 'info')
        return redirect(url_for('facultylogin'))

#=========================================================================
#LOGOUT
@app.route('/logout', methods=['GET', 'POST'])
def logout():
        session.pop('username', None)
        return redirect(url_for('home'))
#==========================================================================
#MAINLOOP

if __name__ == '__main__':
    app.run(host='172.31.77.165', port=5000, debug=True)



