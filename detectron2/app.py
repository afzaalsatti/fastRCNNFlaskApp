from flask import Flask, render_template, request 
import os 
import ffmpeg
import subprocess
import psutil
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
    file_meta_data = ffmpeg.probe(file_path)["streams"]
    faster_r_cnn_response =  fasterRCNN( file_path ) 
    faster_r_cnn_response["response_video_file"] = response_video_file(file_path)
    faster_r_cnn_response["file_meta_data"] = file_meta_data
    # EXTERNAL SYSTEM GPU
    external_gpu = get_external_gpu_details()
    if external_gpu:
        print("External GPU Details:")
        print(external_gpu)
    else:
        external_gpu="null"
        print("No external GPU found.")
    faster_r_cnn_response["external_gpu"] = external_gpu
    if os.path.exists(file_path): 
        remove_video_file(file_path) 
    return {"faster_r_cnn_response":faster_r_cnn_response}
def get_external_gpu_details():
    gpu_details = None

    # Check for available GPUs
    if psutil.WINDOWS:
        try:
            import wmi

            w = wmi.WMI(namespace="root\\CIMV2")
            gpu_info = w.query("SELECT * FROM Win32_VideoController WHERE AdapterCompatibility LIKE '%External%'")

            if gpu_info:
                # Get details of the first external GPU
                gpu = gpu_info[0]
                gpu_details = {
                    "Name": gpu.Name,
                    "Description": gpu.Description,
                    "DeviceID": gpu.DeviceID,
                    # Add more desired details here
                }
        except ImportError:
            pass

    return gpu_details

def remove_video_file(file_path):
    try:
        # Terminate any running ffmpeg processes
        subprocess.run(['taskkill', '/F', '/IM', 'ffmpeg.exe'])

        # Remove the video file
        os.remove(file_path)

        print("Video file removed successfully.")
    except FileNotFoundError:
        print("The video file does not exist.")
    except Exception as e:
        print(f"Error occurred while removing the video file: {e}")

def response_video_file(file_path):
    import base64
    response_base64 = ""
    with open(file_path, "rb") as videoFile:
        base64_data = base64.b64encode(videoFile.read()).decode('utf-8')
        response_base64 = {'base64': base64_data}
        print(response_base64)
    return response_base64
def get_external_gpu_details():
    gpu_details = None

    # Check for available GPUs
    if psutil.WINDOWS:
        try:
            import wmi

            w = wmi.WMI(namespace="root\\CIMV2")
            gpu_info = w.query("SELECT * FROM Win32_VideoController WHERE AdapterCompatibility LIKE '%External%'")

            if gpu_info:
                # Get details of the first external GPU
                gpu = gpu_info[0]
                gpu_details = {
                    "Name": gpu.Name,
                    "Description": gpu.Description,
                    "DeviceID": gpu.DeviceID,
                    # Add more desired details here
                }
        except ImportError:
            pass

    return gpu_details

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)  # Change the port to 8080