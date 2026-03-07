import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

from src.core.base import Email
from src.config.settings import settings

class Gmail(Email):
    def __init__(self) -> None:
        super().__init__(username=settings.gmail.USERNAME)
        self.password = settings.gmail.PASSWORD

    def send(self, receiver: str,
             content: str,
             attachments: Optional[list[str]] = None
             ) -> None:
        """
        Send an email via Gmail SMTP.
        """
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = receiver
        
        # Dynamic subject based on attachment filename or general default
        if attachments and len(attachments) > 0:
            subject = f"Newspaper: {os.path.basename(attachments[0])}"
        else:
            subject = "Newspaper PDF Attachment"
            
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))

        if attachments:
            for file_path in attachments:
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

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, receiver, text)
            server.quit()
            print(f"✅ Email sent successfully to {receiver}!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
