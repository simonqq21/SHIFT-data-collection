from email.message import EmailMessage
import ssl
import smtplib

def send_email(subject, body):
    email_sender = 'pgms.thesis@gmail.com'
    email_password = 'bkpqdjxsjgdemsjw'

    # Add emails here Enter emails here
    email_receivers = ['william_dimaculangan@dlsu.edu.ph', 'simon_justin_que@dlsu.edu.ph']

    # subject = 'Server Potentially Down'
    # body = """
    # Hello world.
    # """
    try:

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = ', '.join(email_receivers)
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        # Define email server, port, and context
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            #login
            smtp.login(email_sender, email_password)
            smtp.send_message(em)
            print("Email sent successfully!")
    except:
        print("Email was not sent.")
