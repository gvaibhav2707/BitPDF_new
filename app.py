from flask import Flask, render_template, request, send_file, redirect, url_for, after_this_request
import os
from werkzeug.utils import secure_filename
from backend import summarize_pdf  

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads/'
SUMMARY_FOLDER = 'summaries/'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SUMMARY_FOLDER'] = SUMMARY_FOLDER

# Function to check allowed file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process PDF using the backend summarization code
        summary_text = summarize_pdf(file_path)
        os.remove(file_path)

        folder = app.config['SUMMARY_FOLDER']
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            os.remove(file_path)

        # Save summary to a text file
        summary_filename = filename.rsplit('.', 1)[0] + '.txt'
        summary_path = os.path.join(app.config['SUMMARY_FOLDER'], summary_filename)
        with open(summary_path, 'w', encoding='utf-8') as summary_file:
            summary_file.write(summary_text)
        return redirect(url_for('download_summary', filename=summary_filename))
    return redirect(request.url)

@app.route('/download/<filename>')
def download_summary(filename):
    response = send_file(os.path.join(app.config['SUMMARY_FOLDER'], filename), as_attachment=True)
    return response
    

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SUMMARY_FOLDER'], exist_ok=True)
    
    app.run(debug=True, use_reloader=True)
