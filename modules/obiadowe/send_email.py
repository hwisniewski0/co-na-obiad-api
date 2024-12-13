from os import getenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_email(content, sender_email):
    try:

        email_address = getenv('EMAIL_ADDRESS')
        email_password = getenv('EMAIL_PASSWORD')
        email_recipient = getenv('EMAIL_RECIPIENT')
        
        if not email_address or not email_password or not email_recipient:
            return False
        


        smtp_server = "smtp.gmail.com"
        smtp_port = 587


        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = email_recipient
        msg['Subject'] = f"Wiadomość od [ {sender_email} ]"

        msg.attach(MIMEText(content, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)

        # Wysyłanie wiadomości
        server.sendmail(email_address, email_recipient, msg.as_string())
        server.quit()

        print("Wiadomość została wysłana.")
        return True
    except Exception as e:
        print(f"Błąd podczas wysyłania wiadomości e-mail: {e}")
        return False