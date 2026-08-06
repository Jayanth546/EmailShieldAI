from email import policy
from email.parser import BytesParser
import re


class EmailParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        with open(self.file_path, "rb") as file:
            message = BytesParser(policy=policy.default).parse(file)

        body = ""
        html = ""
        urls = []
        attachments = []

        if message.is_multipart():
            for part in message.walk():

                content_type = part.get_content_type()
                disposition = part.get_content_disposition()

                if disposition == "attachment":
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)

                elif content_type == "text/plain":
                    body += part.get_content()

                elif content_type == "text/html":
                    html += part.get_content()

        else:
            body = message.get_content()

        # Extract URLs
        urls = re.findall(r"https?://[^\s<>\"']+", body)

        return {
            "from": message.get("From"),
            "to": message.get("To"),
            "subject": message.get("Subject"),
            "date": message.get("Date"),
            "message_id": message.get("Message-ID"),
            "reply_to": message.get("Reply-To"),
            "return_path": message.get("Return-Path"),

            # NEW
            "authentication_results": message.get(
                "Authentication-Results"
            ),
            "received_spf": message.get(
                "Received-SPF"
            ),
            "dkim_signature": message.get(
                "DKIM-Signature"
            ),
            "received": message.get_all(
                "Received", []
            ),

            "body": body,
            "html": html,
            "urls": urls,
            "attachments": attachments,
        }
