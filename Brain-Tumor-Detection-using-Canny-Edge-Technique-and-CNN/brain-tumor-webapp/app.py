import os
from flask import Flask, flash, request, redirect, url_for,render_template
from werkzeug.utils import secure_filename
from braintum import *

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY']='mykey'



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(request):
    if 'file' not in request.files:
        flash('No file!')
        return redirect(request.url)

    file = request.files['file']
  
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filename)
        data = request.files['file']
        return data, filename





@app.route('/', methods=['GET', 'POST'])
def upload_file():  
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():

        data, filename = validate_file(request)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print(file.filename)
        image_detect('./static/'+str(file.filename))
        return render_template('prediction.html')


    
if __name__ == '__main__':
  app.run(debug=True)