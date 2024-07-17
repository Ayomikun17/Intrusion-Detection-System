# Importing dependencies
import time
import cv2
import pyttsx3
import cvzone
from cvzone.FaceDetectionModule import FaceDetector
import os
from email.message import EmailMessage
import ssl
import smtplib

cap = cv2.VideoCapture(0)
face_detector = FaceDetector(minDetectionCon=0.6)
engine = pyttsx3.init()
image_counter = 0
image_paths = []
image_directory = 'intruder_images'

# Create the directory if it doesn't exist
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

# Function to send intrusion email
def send_mail(image_paths):
    # Sending the email to the property owner
    email_sender = 'olaemma657@gmail.com'
    email_password = os.environ.get("EMAIL_PASSWORD")
    email_receiver = 'emmanuel.olademehin@stu.cu.edu.ng'

    # Mail details
    email_subject = 'Test email for intruder detection'
    email_body = """
    Urgent! There seems to be a possible break-in at your property. 
    Attached are the images of the intruder.
    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = email_subject
    em.set_content(email_body)

    # Attach the images
    for image_path in image_paths:
        with open(image_path, 'rb') as img:
            em.add_attachment(img.read(), maintype='image', subtype='jpeg', filename=os.path.basename(image_path))

    # SSL for layer of security on the internet
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Image Capturing

while cap.isOpened():
    ret, frame = cap.read()
    frame, faces = face_detector.findFaces(frame)

    if ret:
        cv2.imshow('Video', frame)

    if faces:
        image_counter += 1
        image_path = os.path.join(image_directory, f'face_{image_counter}.jpg')
        cv2.imwrite(image_path, frame)
        image_paths.append(image_path)
        engine.say('Intruder Alert')
        engine.runAndWait()

        if image_counter >= 2:
            send_mail(image_paths)
            image_paths.clear()
            image_counter = 0
        time.sleep(15)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
