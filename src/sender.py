import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Config
sender_email = "abhijithmallya@gmail.com"
app_password = "<#app_password_here#>"  # Generate at myaccount.google.com/apppasswords
receiver_email = "glenndsouza1911@gmail.com "
file_path = "/home/user/vartabharathi/Udayavani_Manipal_20260101.pdf"  # Path to your PDF file

# Create message
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "Udayavani Manipal PDF Attachment"

body = "Here's the Udayavani Manipal edition PDF for 01-01-2026!"
msg.attach(MIMEText(body, 'plain'))

# Attach PDF
if os.path.exists(file_path):
    with open(file_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename={os.path.basename(file_path)}'
    )
    msg.attach(part)
else:
    print(f"File {file_path} not found!")

# Send via Gmail SMTP
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(sender_email, app_password)
text = msg.as_string()
server.sendmail(sender_email, receiver_email, text)
server.quit()

print("Email sent successfully!")
