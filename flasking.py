import os
from flask import Flask,render_template,request,flash,url_for,redirect,sessions,session
from flask_mysqldb import MySQL
import random

import sms

#global variables

otp1='none'
studentTableName='studentlogininfo'
facultyTableName='facultylogininfo'


app=Flask(__name__)

#mysql initialistaions

app.config['SECRET_KEY']='AjJ0lXaX5K9tai8QsUhwwQ'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Anant@1707'
app.config['MYSQL_DB']='collegeplus'
msql=MySQL(app)

#routes
@app.route('/')
def home():

   return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    cur=msql.connection.cursor()
    if request.method=='POST':
        logininfo=request.form
        fname=logininfo['fname']
        lname=logininfo['lname']
        email=logininfo['email']
        sid=logininfo['sid']
        phone=logininfo['phone']
        password=logininfo['password']
        confirmpassword=logininfo['confirmpass']

        values=(fname,lname,sid,email,password,phone)
        if(password==confirmpassword):
            flash("thanks for registering", 'success')
            cur.execute("INSERT INTO " +studentTableName+ " VALUES" + "(%s,%s,%s,%s,%s,%s)",values)
            msql.connection.commit()
            cur.close()
            return redirect(url_for('home'))
        else:
            flash("Password didnt match",'danger')
            return redirect(url_for('register'))


    return render_template('register.html')

#after user logs in
@app.route('/loggedin')
def loggedin():


    return render_template('original_regna.html')


#user profile page

@app.route('/profile', methods=['GET','POST'])
def profile():
    if request.method=='POST':
        session.pop('username',None)
        return redirect(url_for('home'))


    cur = msql.connection.cursor()
    ssid=session.get('username')
    cur.execute(f"select * from studentlogininfo where sid={ssid}")
    a=cur.fetchone()
    name=a[0]+" "+a[1]
    email=a[3]
    phonenumber=a[5]


    return render_template('profile.html',name=name,email=email,phonenumber=phonenumber)





@app.route('/student',methods=['GET','POST'])
def studentlogin():
    cur = msql.connection.cursor()
    if request.method=='POST':
        slogininfo=request.form
        ssid=slogininfo['sid']
        password=slogininfo['password']
        cur.execute(f"SELECT sid FROM {studentTableName} ")
        a=cur.fetchall()
        flag=0
        for x in a:
            if (str(x[0])==ssid):
                flag+=1

        if flag==0:
            flash("You are not registered!!,REGISTER NOW",'danger')
            return redirect(url_for('register'))
        elif flag!=0:
            cur.execute(f"SELECT passwordd FROM {studentTableName} where sid = '{ssid}'")
            a=cur.fetchall()
            print(password)
            print(a[0][0])

            if (password==a[0][0]):


                session['logged_in']=True
                session['username'] = ssid
                cur.execute(f"SELECT fname FROM {studentTableName} where sid = '{ssid}'")
                fname=cur.fetchall()

                flash(f'welcome {fname[0][0]}','success')

                cur.close()
                return redirect(url_for('loggedin'))
            else:
                flash("WRONG PASSWORD",'danger')
                cur.close()
                return redirect(url_for('studentlogin'))

    return render_template("student-login.html")

@app.route('/forgot',methods=['GET','POST'])
def forgotpw():
    global otp1
    cur=msql.connection.cursor()
    if request.method=='POST':
        slogininfo = request.form
        ssid = slogininfo['sid']
        cur.execute(f"SELECT sid FROM {studentTableName} ")
        a = cur.fetchall()
        flag = 0
        for x in a:
            if (str(x[0]) == ssid):
                flag += 1

        if flag == 0:
            flash("You are not registered!!,REGISTER NOW", 'danger')
            return redirect(url_for('register'))
        elif flag != 0:

            otp1=str(random.randrange(100000,999999))


            URL = 'https://www.way2sms.com/api/v1/sendCampaign'
            cur.execute(f"SELECT phone FROM {studentTableName} where sid= {ssid}")
            a=cur.fetchall()[0][0]
            #sms.sendPostRequest(URL, 'Q9RT7DGYM9XI20C4K0ZGTPC771YVIFZL', 'ZP28KI0MG95EYE7H', 'stage', a, '8437008949', "Your OTP (One Time Password) to change your password is: "+str(otp1)+"Do not share this with anyone!   Team college+")
            return redirect(url_for('resetpass',phonenumber=a))

    return render_template('forgot.html')

@app.route('/reset<phonenumber>',methods=['GET','POST'])
def resetpass(phonenumber):
    cur = msql.connection.cursor()
    print(otp1)
    if request.method == 'POST':
        slogininfo = request.form
        ootp = slogininfo['otp']
        print(ootp)


        if ootp==(otp1):
            return redirect(url_for('newpass',phonenumber2=phonenumber))
        else:
            flash('INVALID OTP','danger')
            return redirect(url_for('resetpass',phonenumber=phonenumber))

    return render_template('reset.html')

@app.route('/newpass<phonenumber2>',methods=['GET','POST'])
def newpass(phonenumber2):
    cur = msql.connection.cursor()
    if request.method == 'POST':
        slogininfo = request.form
        newpassword= slogininfo['password']
        confirmnewpassword=slogininfo['cpassword']
        print(newpassword,confirmnewpassword)
        if(newpassword==confirmnewpassword):


            query=f" UPDATE  {studentTableName}  set passwordd = '{newpassword}' where phone =  {phonenumber2}  ; "

            cur.execute(query)
            msql.connection.commit()
            return redirect(url_for('studentlogin'))
        else:
            flash("passwords didnt match",'danger')
            return redirect(url_for('newpass',phonenumber2=phonenumber2))
    return render_template('newpass.html')

@app.route('/faculty',methods=['GET','POST'])
def facultylogin():
    cur=msql.connection.cursor()
    if request.method=='POST':
        flogininfo=request.form
        username=flogininfo['logid']
        password=flogininfo['password']
        print(username,password)
        cur.execute(f"select passwordd from {facultyTableName} where loginid= '{username}'")
        a=cur.fetchall()[0][0]
        print(a)
        if password==a:
            return redirect(url_for('home'))
        else:
            flash('invalid username or password')
    return render_template('faculty-login.html')



#function mainloop
if __name__=='__main__':
    app.run(host='172.31.74.44',port=5000,debug=True)

