from flask import Flask, render_template, request 
import os 
#import helper methods 
from faster_r_cnn import run as fasterRCNN 
 
app = Flask(__name__) 
@app.route("/") 
def index_page(): 
    return render_template('index.html') 
 
@app.route('/upload_file', methods=['POST']) 
def upload_file(): 
    if 'file' not in request.files: 
        return 'No file uploaded.', 400 
     
    file = request.files['file'] 
    if file.filename == '': 
        return 'Empty filename.', 400 
    # Specify the folder name you want to create 
    folder_name = 'temp_uploads' 
 
    # Get the current working directory 
    current_directory = os.getcwd() 
 
    # Create the folder path by joining the current directory and folder name 
    folder_path = os.path.join(current_directory, folder_name) 
    # Create the folder 
    os.makedirs(folder_path, exist_ok=True) 
 
    # Save the uploaded file to the specified folder 
    file_path = os.path.join(folder_path, file.filename) 
    file.save(file_path) 
    faster_r_cnn_response =  fasterRCNN( file_path ) 
    if os.path.exists(file_path): 
        os.remove(file_path) 
    return {"data":faster_r_cnn_response}