# Smart Vitrine Glass
# Developed by Zhixin Lin

# Import openCv, time, and pySerial libraries
import cv2
import time
import serial

# Set up serial port, wait 2 seconds so that Arduino would have finished initialization
ser1 = serial.Serial('COM3', 9600)
time.sleep(2)

# Threshold to detect object
thres = 0.60

# Initialize video capture source
cap = cv2.VideoCapture(1)
# Set video capture resolution if the USB camera supports it
# cap.set(3,1280)
# cap.set(4,720)

# Read the object class names into a list
classNames= []
classFile = 'coco.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

# Initialize the model weights path
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

# Set up the object detection model
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Time counter for glass reset delay
counter = 0
# Turn on the glass
ser1.write("1".encode())
# Initialize the status of the class
isOn = True

# Execute detection for each frame
while True:
    success,img = cap.read()
    classIds, confs, bbox = net.detect(img,confThreshold=thres)

    # Draw boxes and labels if objects are detected
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(),confs.flatten(),bbox):
            # Draw red box if cell phone is detected
            if classNames[classId - 1].upper() == "CELL PHONE":
                cv2.rectangle(img, box, color=(0, 0, 255), thickness=2)
                cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 300, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            # Draw green box if other object is detected
            else:
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    # Send turn off serial data to arduino if it is cell phone is detected
    if 77 in classIds and isOn:
        print("phone detected, turn off glass")
        ser1.write("0".encode())
        counter = 0
        isOn = False
    # Reset time counter if cell phone is detected and glass is already opaque
    elif 77 in classIds:
        print("phone detected, glass is already off")
        counter = 0

    # Turn on the glass again after seconds of delay
    if counter == 10:
        if 77 not in classIds:
            print("turn on glass again")
            ser1.write("1".encode())
            isOn = True
        counter = 0
    elif not isOn:
        counter += 1

    print(counter)

    # Render the annotated video frame
    cv2.imshow("Output",img)

    # Quit trigger
    if cv2.waitKey(2) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

