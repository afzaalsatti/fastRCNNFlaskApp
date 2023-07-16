print("starting imports")
import torch
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.config import get_cfg
import cv2
import psutil
import time
import copy
import os
print("imports done")
def run(video_path):
    objects_detected = {}
    frames_count = 0
    processing_time = 0
    input_fps = 0
    detailed_output =[]
    accuracy = []
    # Initialize variables for tracking CPU, memory, and GPU usage
    cpu_usage_list = []
    mem_usage_list = []
    gpu_usage_list = []
    print("starting faster r cnn demon")
    # Step 2: Prepare the video
    cpu_usage = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    mem_usage = mem.used / mem.total * 100
    start_time = time.time()
    cpu_usage_list.append(cpu_usage)
    mem_usage_list.append(mem_usage)
    # Step 3: Initialize the Detectron2 model
    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    # Check if running inside a Docker container
    if 'DOCKER_CONTAINER' in os.environ:
        # Set the file path within the container
        cfg_file_path = '/home/configs/COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml'
    else:
        # Set the file path for local development
        cfg_file_path = 'configs/COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml'
    cfg.merge_from_file(cfg_file_path)  # Path to the model's config file
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Set a threshold for object detection confidence
    cfg.MODEL.WEIGHTS = "detectron2://COCO-Detection/faster_rcnn_R_101_FPN_3x/137851257/model_final_f6e8b1.pkl"  # Path to the model's weights
    print("finished faster r cnn cfg")
    # Step 4: Process each frame
    class_names = MetadataCatalog.get(cfg.DATASETS.TEST[0] if len(cfg.DATASETS.TEST) else "__unused").thing_classes
    video = cv2.VideoCapture(video_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print("finished video frame loading")
    predictor = DefaultPredictor(cfg)
    for frame_num in range(num_frames):
        cpu_usage_list.append(cpu_usage)
        mem_usage_list.append(mem_usage)
       # processing_time += result.speed["inference"]
        detected_Objects={}
        frames_count+=1;
        print("processing frame", frames_count , "/", num_frames)
        frame_info = {"frame_number":frames_count, "detected_Objects":{} }
        ret, frame = video.read()
        if not ret:
            break

        # Step 5: Perform object detection on each frame
        output = predictor(frame)
        print("prediction done for frame")
        instances = output["instances"]
        boxes = instances.pred_boxes.tensor.numpy().tolist()
        scores = instances.scores.numpy().tolist()
        classes = instances.pred_classes.numpy().tolist()
        identified_frame_object = {}
        axis = []
        index = 0
        print(classes)
        for classId in classes:
            accuracy.append(scores[index]);
            class_name = class_names[int(classes[index])]
            if class_name not in identified_frame_object:
                identified_frame_object[class_name] = 1
                if class_name in objects_detected:
                    objects_detected[class_name] += 1  # Update value for 'key1'
                    
                else:
                    objects_detected[class_name] = 1  # Insert new object for 'key1'
            else:
                identified_frame_object[class_name] += 1
            axis.append({class_name: boxes[index]})
            index = index + 1
        frame_info["detected_Objects"] = identified_frame_object
        frame_info["axis"] = axis
        detailed_output.append(frame_info)
    end_time = time.time()
    for detected_object_class in objects_detected.keys():
        frame_visibility_duration = int(objects_detected.get(detected_object_class))/fps
        objects_detected[detected_object_class] = frame_visibility_duration
    cpu_usage = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    mem_usage = mem.used / mem.total * 100
    import platform
    uname = platform.uname()
    # Calculate elapsed time and output frame rate
    elapsed_time = end_time - start_time
    frame_rate = frames_count / elapsed_time
    # Calculate average usage
    avg_cpu_usage = sum(cpu_usage_list) / len(cpu_usage_list)
    avg_mem_usage = sum(mem_usage_list) / len(mem_usage_list)

    server_response = {}
    print("-------------------Strating Faster log--------------------------")
    print("-------------------System Information--------------------------")
    print(f"System: {uname.system}")
    print(f"Release: {uname.release}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")
    server_response["system_info"] = {"system":uname.system, "release":uname.release,"machine":uname.machine}
    
    print("-------------------Resource Usage--------------------------")

    # Print average usage
    print(f'Average CPU usage: {avg_cpu_usage:.2f}%')
    print(f'Average memory usage: {avg_mem_usage:.2f}%')
    server_response["resource_usage"] = {"cpu_usage":avg_mem_usage, "memory":avg_mem_usage}
    #for i, usage in enumerate(avg_gpu_usage):
        #print(f'Average GPU {i+1} usage: {usage:.2f}%')

    print("-------------------Time Consumption--------------------------")
    print(f'Start Time: {start_time:.2f}s')
    print(f'End Time: {end_time:.2f}s')
    print(f'Elapsed time: {elapsed_time:.2f} s')
    processing_time = processing_time/1000
    print(f'Total Processing Time:{processing_time:.2f}s')
    server_response["time_consumption"] = {"start_time":start_time, "end_time":end_time
                                          , "elapsed_time":elapsed_time, "processing_time":processing_time}

    print("-------------------Frame Rate--------------------------")
    print("frames count:",frames_count)
    print(f'Input Frame rate: {fps:.2f} fps')
    print(f'Output Frame rate: {frame_rate:.2f} fps')
    server_response["frames_info"] = {"frames_count":frames_count,"input_frame_rate":fps, "output_frame_rate":frame_rate}

    print("-------------------Object Detection--------------------------")
    print("detections:",objects_detected)
    average_conf = sum(accuracy)/len(accuracy)
    print(f'Accuracy conf: {average_conf:.2f} %')
    print("Detailed Output For Graphs",detailed_output)
    server_response["object_detection"] = {"detections":objects_detected, "average_conf":average_conf, "detailed_output":detailed_output}
    print("-------------------End faster r cnn log--------------------------")
    return server_response


def main():
    run(**vars())


if __name__ == '__main__':
    main()