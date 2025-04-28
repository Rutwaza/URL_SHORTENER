from flask import Flask, render_template, request, redirect
from models import db, URL
from utils import generate_short_code

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_code = generate_short_code()

        # Check if short_code already exists
        while URL.query.filter_by(short_code=short_code).first() is not None:
            short_code = generate_short_code()

        new_url = URL(original_url=original_url, short_code=short_code)
        db.session.add(new_url)
        db.session.commit()

        return render_template('success.html', short_code=short_code)

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_original(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        url.visits += 1
        db.session.commit()
        return redirect(url.original_url)
    else:
        return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
