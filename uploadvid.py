import os
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = set(['wav', 'mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',
                                        filename=filename))
            else:
                flash('List of supported extensions: .wav, .mp4')
                return redirect(request.url)
    return render_template('uploadforminit.html')

if __name__ == '__main__':
    app.run(debug=True)
