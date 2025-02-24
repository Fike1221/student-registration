import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Define the email sender and recipient
sender_email = "fikadumom@gmail.com"
# receiver_email = 'mulugetateamrat9@gmail.com'
password = "crgr rfak kkbc xyvb"  # App password if using Gmail



def send_email(receiver_email, message_to_be_sent, subject):
    try:

# Create the email message
        message = MIMEMultipart()

        # start simple mail transfer protocol server 
        server = smtplib.SMTP('smtp.gmail.com', 587)

        message['From'] = 'Fike-Online-Banking'
        message['To'] = receiver_email
        message['Subject'] = subject

        # Email body
        body = message_to_be_sent

        # Attach the body with the email
        message.attach(MIMEText(body, 'plain'))

        # Set up the SMTP server (this example uses Gmail's server)

        server.starttls()  # Secure connection

        # Log in to the server
        server.login(sender_email, password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

        # Close the server connection
        server.quit()

    except Exception:
        return False
    



def random_id():
    """Returns random id numbers of digit 6 with type int"""
    return random.randint(100000, 999999)

def generate_salary():
    """Generates random number just to represent salary! Shouldn't be used for real apps"""
    return random.randint(10000, 20000)

def generate_grade(mark):
    grade = ""
    point = None
    if mark >= 90:
        grade = "A+"
        point = 4.0
    elif mark >= 85:
        grade = "A"
        point = 4.0
    elif mark >= 80:
        grade = "A-"
        point = 3.75
    elif mark >= 75:
        grade = "B+"
        point = 3.5
    elif mark >= 70:
        grade = "B"
        point = 3.0
    elif mark >= 65:
        grade = "B-"
        point = 2.75
    elif mark >= 50:
        grade = "C"
        point = 2.0
    elif mark >= 30:
        grade = "D"
        point = 1.0
    else:
        grade = "F"
        point = 0.0
    return [grade, point]
    