import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipients, subject, message):
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # add gmail.com
    recps = []
    for rec in recipients:
        if not '@' in rec:
            recps.append( rec + '@gmail.com')
        else:
            recps.append(rec)
    recipients =recps

    # start TLS for security
    s.starttls()

    # Authentication
    sender = ""
    passwd = ""
    s.login(sender, passwd)

    # message to be sent
    #message = "Message_you_need_to_send"
    msg = MIMEText('<font size="5">'+message+'</font>', 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    # sending the mail
    s.sendmail("thermic.tv@gmail.com", recipients, msg.as_string())

    # terminating the session
    s.quit()

#send_email(['joigno@gmail.com'], 'CRYPTO ALERT 2: BLABLA')