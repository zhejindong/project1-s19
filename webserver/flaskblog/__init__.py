from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zd2221:rw3ifzZu7E@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/w4111' 


from flaskblog import routes
