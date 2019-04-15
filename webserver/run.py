from flaskblog import app
from flaskblog import db

if __name__ == '__main__':
     app.run(debug=True)
     db.create_all()