from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask import  g, Response
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from datetime import datetime

global current_user_email
current_user_email=[]

DB_USER = "zd2221"
DB_PASSWORD = "rw3ifzZu7E"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

engine=create_engine('postgresql://zd2221:rw3ifzZu7E@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/w4111')

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

posts = set()

@app.route("/")
@app.route("/home",methods=['GET'])
def home():
    cmd='SELECT * FROM item';
    cursor = g.conn.execute(text(cmd))
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       posts.add(pos)
    return render_template('home.html',posts=posts,current_user_email=current_user_email)


@app.route("/mycart",methods=['GET'])
def mycart():
    if current_user_email:
        carts=set()
        flash('Quick clean your cart','success')
        cmd='select seller_name,item_id,price1,price2,seller_table.seller_id as seller_id from item_seller,seller_table where item_seller.seller_id=seller_table.seller_id and item_id in (select item_id from costomer_cart where email=:email1);'
        cursor = g.conn.execute(text(cmd),email1=current_user_email[0])
        item= cursor.fetchall()# can also be accessed using result[0]
        #flash(item)
        cursor.close()
        for i in item:
            pos=()
            pos=(i.item_id,i.seller_name,i.price1,i.price2,i.seller_id)
            carts.add(pos)
        return render_template('mycart.html',posts=carts,current_user_email=current_user_email)
    else:
        flash("Log in please :)",'warn')
        return redirect(url_for('login'))



@app.route("/myorder",methods=['GET'])
def myorder():
    if current_user_email:
        orders=set()
        flash('Here is your order','success')
        cmd='select * from order_table where order_id in (select order_id from costomer_order where email=:email1);'
        cursor = g.conn.execute(text(cmd),email1=current_user_email[0])
        order= cursor.fetchall()# can also be accessed using result[0]
        #flash(order[0][1])
        cursor.close()
        for i in order:
             pos=()
             pos=(i[0],i[1],i[2])
             orders.add(pos)
        #flash(orders)
        return render_template('myorder.html',posts=orders,current_user_email=current_user_email)
    else:
        flash("Log in please :)",'warn')
        return redirect(url_for('login'))



@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account created')
        # insert into database:
        name = request.form['username']
        email= request.form['email']
        password=request.form['password']
        print name
        cmd = 'INSERT INTO costomer(user_name,email,password) VALUES (:name1,:email1,:password1)';
        g.conn.execute(text(cmd),name1 = name,email1=email,password1=password);
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_in=request.form['email']
        current_user_email.append(email_in)
        password_in=request.form['password']
        cmd='SELECT password FROM costomer where email=:email1';
        cursor = g.conn.execute(text(cmd),email1=email_in)
        passwordt= cursor.fetchall()[0]# can also be accessed using result[0]
        cursor.close()
        #user = User(request.form['email'],passwordt)
        if form.password.data == passwordt[0]:
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title='Login', form=form, current_user_email=current_user_email)


@app.route("/logout")
def logout():
    global current_user_email
    current_user_email=[]
    #flash(current_user_email)
    flash("Log Out:)", 'success')
    return redirect(url_for('home'))
    #return render_template('logout.html', title='Logout')

@app.route("/account", methods=['GET'])
def account():
    form={}
    if current_user_email:
        form["email"] = current_user_email[-1]
        cmd='SELECT * FROM costomer where email=:email1';
        cursor = g.conn.execute(text(cmd),email1=form["email"])
        user= cursor.fetchall()[0]# can also be accessed using result[0]
        cursor.close()
        form["username"]=user[0]
        #flash(user[0])
        #return redirect(url_for('home'))
        return render_template('account.html', title='Account',form=form, current_user_email=current_user_email)
    else:
        flash("You need to login")
        redirect(url_for('login'))
        return redirect(url_for('home'))


@app.route("/post/<int:post_id>")
def post(post_id):
    items=set()
    cmd='select seller_name,item_id,price1,price2,seller_table.seller_id as seller_id,item_no from item_seller,seller_table where item_seller.seller_id=seller_table.seller_id and item_no=:item_no1 order by price2;'
    cursor = g.conn.execute(text(cmd),item_no1=post_id)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=(i.item_id,i.seller_name,i.price1,i.price2,i.seller_id,i.item_no)
       items.add(pos)
    return render_template('post.html',posts=items,current_user_email=current_user_email)


@app.route("/post/<int:post_id>/<int:item_id>/cart", methods=['GET', 'POST'])
def Cart(post_id,item_id):
    if current_user_email:
        flash('Item has been added to cart!', 'success')
        cmd='insert into costomer_cart values(:email1,:item_id1);'
        cursor = g.conn.execute(text(cmd),email1=current_user_email[-1],item_id1=item_id)
        return redirect(url_for('post',post_id=post_id))
    else:
        flash("Log in please:)",'fail')
        return redirect(url_for('login'))


@app.route("/post/<int:post_id>/<int:item_id>/purchase", methods=['GET', 'POST'])
def Purchase(post_id,item_id):
    if current_user_email:
        flash('Your order is placed :)', 'success')
        cmd='insert into costomer_order values(:email1);'
        cursor = g.conn.execute(text(cmd),email1=current_user_email[-1])
        cmd='select max(order_id) from costomer_order'
        cursor = g.conn.execute(text(cmd))
        order_id= cursor.fetchall()[0]
        cmd='insert into order_table values(:order1,CURRENT_TIMESTAMP);'
        cursor = g.conn.execute(text(cmd),order1=order_id[0])
        cmd='insert into order_item values(:order1,:item_id1);'
        cursor = g.conn.execute(text(cmd),order1=order_id[0],item_id1=item_id)
        return redirect(url_for('post',post_id=post_id))
    else:
        flash("Log in please:)",'fail')
        return redirect(url_for('login'))

@app.route("/delete/<int:item_id>")
def delete(item_id):
    cmd='delete from costomer_cart where email=:email1 and item_id=:item1;'
    cursor = g.conn.execute(text(cmd),email1=current_user_email[-1],item1=item_id)
    return redirect(url_for('mycart'))


@app.route("/cloth")
def cloth():
    cloths=set()
    a='Cloth'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       cloths.add(pos)
    return render_template('home.html',posts=cloths,current_user_email=current_user_email)


@app.route("/book")
def book():
    book=set()
    a='Books & Audible'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       book.add(pos)
    return render_template('home.html',posts=book,current_user_email=current_user_email)


@app.route("/sports")
def sports():
    sports=set()
    a='Sports'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       sports.add(pos)
    return render_template('home.html',posts=sports,current_user_email=current_user_email)

@app.route("/food")
def food():
    food=set()
    a='Food'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       food.add(pos)
    return render_template('home.html',posts=food,current_user_email=current_user_email)

@app.route("/home1")
def home1():
    home1=set()
    a='Home'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       home1.add(pos)
    return render_template('home.html',posts=home1,current_user_email=current_user_email)

@app.route("/beauty")
def beauty():
    beauty=set()
    a='Beauty'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       beauty.add(pos)
    return render_template('home.html',posts=beauty,current_user_email=current_user_email)

@app.route("/movie")
def movie():
    movie=set()
    a='Movie'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       movie.add(pos)
    return render_template('home.html',posts=movie,current_user_email=current_user_email)

@app.route("/office")
def office():
    office=set()
    a='Office & Electronics'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       office.add(pos)
    return render_template('home.html',posts=office,current_user_email=current_user_email)

@app.route("/pet")
def pet():
    pet=set()
    a='Pet Supplies'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       pet.add(pos)
    return render_template('home.html',posts=pet,current_user_email=current_user_email)

@app.route("/toys")
def toys():
    toys=set()
    a='Toys'
    cmd='select * from item where item_no in (select item_no from item_category where name=:name1);'
    cursor = g.conn.execute(text(cmd),name1=a)
    item= cursor.fetchall()# can also be accessed using result[0]
    cursor.close()
    for i in item:
       pos=()
       pos=(i.discription,i.picture,i.item_no)
       toys.add(pos)
    return render_template('home.html',posts=toys,current_user_email=current_user_email)



