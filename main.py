#-------------------------------------Required module
from flask import Flask, render_template,request,redirect,url_for,session,make_response,flash
import sqlite3
#--------------------------------Flask object
app = Flask(__name__)
app.secret_key='yyyyy@123456789'
#------------------------------global variable----------------
table_name=''
db_path='reg_data.db'
#----------------regitration function-------------------------------------------
def Registration(data):
    try:
        way=sqlite3.connect(db_path)
        key = way.cursor()
        key.execute("INSERT INTO regis (name,email,password) VALUES (?,?,?)",(data['name'],data['email'],data['password']))
        unique_id=data['email'].split('@')[0]	    
        key.execute(f"CREATE TABLE {unique_id}(id INTEGER PRIMARY KEY AUTOINCREMENT,title VARCHAR2(20),subject VARCHAR2(20),description VARCHAR2(100),deadline VARCHAR2(20))",)
        way.commit()
        task=True      
    except sqlite3.IntegrityError:
        task=False
    return task    

#-----------------------------------login function---------------------------------------
def log(data):
    way=sqlite3.connect(db_path)
    key = way.cursor()	    
    key.execute(f"select * from regis where email='{data['email']}'")
    info=key.fetchall()
    if len(info)==0:
        task=(False,False)
    else:
        if info[0][2]==data['password']:
            task=(True,True,info[0])
        else:
            task=(True,False) 
    return task          
    
        
@app.route('/',methods=['GET'])
def home():
    global table_name
    user=request.cookies.get('users')
    if user:
        table_name=user.split('@')[0]
        way=sqlite3.connect(db_path)
        key = way.cursor()
        key.execute(f"select * from regis where email='{user}'")
        user_info=key.fetchall()[0]
        session['username']={'name':user_info[0],'email':user_info[1]}
        key.execute(f"select * from {table_name}")
        entries_data=key.fetchall()
        return redirect(url_for('welcome',name=session['username']['name'],data=entries_data,length=len(entries_data)))
    return render_template('home.html')
    
@app.route('/contact',methods=['GET','POST'])
def contact():
    result=None
    if (request.method)=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        comment=request.form.get('cmnt') 
        way=sqlite3.connect(db_path)
        key = way.cursor()
        key.execute("INSERT INTO contacts (name,email,comment) VALUES (?,?,?)",(name,email,comment))
        way.commit()
        result='Query submitted'
    return render_template('contact.html',result=result)


@app.route('/signup',methods = ['GET', 'POST'])
def signup():
    rspns=None
    if(request.method=='POST'):
        print('ys')
        name=request.form.get('fname')+' '+request.form.get('lname')
        email=request.form.get('email')
        pswd=request.form.get('password')
        data={'name':name,'email':email,'password':pswd}
        regis_result=Registration(data)
        if regis_result==True:
            rspns='registered successfull'
        elif regis_result==False:
            rspns='Id already exist'
        else:
            rspns='registration failed'     
    return render_template('signup.html',result=rspns)

@app.route('/login',methods = ['GET', 'POST'])
def login():
    global table_name
    rspns=None
    if 'username' in session:
        return redirect(url_for('welcome',name=session['username']['name']))
    if(request.method=='POST'):
        email=request.form.get('email')
        pswd=request.form.get('password')
        remember=request.form.get('remember')
        data={'email':email,'password':pswd}
        login_result=log(data)
        if login_result[0]==login_result[1]==True:
            user_info=login_result[2]
            table_name=data['email'].split('@')[0]
            session['username']={'name':user_info[0],'email':user_info[1]}
            if remember:
               resp=make_response(redirect(url_for('welcome',name=session['username']['name'])))
               resp.set_cookie('users',user_info[1],max_age=500)
               return resp
            return redirect(url_for('welcome',name=session['username']['name']))
        elif login_result[0]==True and login_result[1]==False:
            rspns='wrong password'
        elif login_result[0]==False:
            rspns='wrong id'
        else:
            rspns='something went wrong'
    return render_template('login.html',result=rspns)

@app.route('/welcome/<string:name>',methods = ['GET','POST'])   
def welcome(name):
    global table_name
    if 'username' in session:
        way=sqlite3.connect(db_path)
        key = way.cursor()
        table_name=session['username']['email'].split('@')[0]
        key.execute(f"select * from {table_name}")
        entries_data=key.fetchall()
        Id=request.args.get('id')
        if Id:
            key.execute(f"delete from {table_name} where id={Id}")
            way.commit()
        return render_template('welcome.html',name=session['username']['name'],data=entries_data,length=len(entries_data))
    else:
        return redirect(url_for('login'))

@app.route('/add',methods = ['GET', 'POST'])   
def add():
    result=None
    if 'username' in session:
        if(request.method=='POST'):
            Title=request.form.get('title')
            Subject=request.form.get('subject')
            Desc=request.form.get('description')
            Dl=request.form.get('deadline')  
            way=sqlite3.connect(db_path)
            key = way.cursor()
            key.execute(f"INSERT INTO {table_name} (title,subject,Description,deadline) VALUES (?,?,?,?)",(Title,Subject,Desc,Dl))
            way.commit()
            result="Sucessfully added"
        return render_template('add.html',result=result,name=session['username']['name'])
    else:
        return redirect(url_for('login'))

    
@app.route('/update',methods = ['GET', 'POST'])   
def update():
    result=None
    exist=False
    if 'username' in session:
        Id=request.args.get('id')
        if(request.method=='POST'):        
            Deadline=request.form.get('deadline')
            way=sqlite3.connect(db_path)
            key = way.cursor()
            key.execute(f"update {table_name} set deadline=? where id=?",(Deadline,Id))
            way.commit()
            result="Sucessfully updated"
        return render_template('update.html',result=result,name=session['username']['name'])
    else:
        return redirect(url_for('login'))
    
        
@app.route('/logout',methods = ['GET', 'POST'])   
def Logout():
    global table_name
    session.pop('username',None)
    resp=make_response(redirect(url_for('login')))
    resp.set_cookie('users','CEO',max_age=0)
    table_name=None
    return resp  
app.run(debug=True)
