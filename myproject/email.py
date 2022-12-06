import os

from django.core.mail import EmailMessage
from django.core.mail.message import SafeMIMEMultipart, SafeMIMEText
from django.utils.encoding import smart_str

from myproject import settings


class EmailHTML(EmailMessage):
    multipart_subtype = "related"
    html = None
    related_ids = []

    def message(self):
        if self.html:
            for id in self.related_ids:
                self.html = self.html.replace(id, "cid:" + id)
            encoding = self.encoding or settings.DEFAULT_CHARSET
            ha = SafeMIMEText(self.html, "html", encoding)
            if self.body:
                a = SafeMIMEMultipart(_subtype="alternative")
                a.attach(
                    SafeMIMEText(smart_str(self.body, encoding), self.content_subtype, encoding)
                )
                a.attach(ha)
            else:
                a = ha
            self.attachments.insert(0, a)
            self.body = None
            self.html = None
        return super(EmailHTML, self).message()

    def attach_html(self, html):
        """
        Specify HTML to include in the message.
        """
        self.html = html

    def attach_related(self, path, mimetype=None):
        """
        Attaches a file from the filesystem, with a Content-ID.
        For use with multipart/related messages.
        """
        filename = os.path.basename(path)
        content = open(path, "rb").read()
        self.attachments.append((filename, content, mimetype, True))
        self.related_ids += [filename]

    def _create_attachment(self, filename, content, mimetype=None, with_id=False):
        """
        Convert the filename, content, mimetype triple into a MIME attachment
        object. Adjust headers to use Content-ID where applicable.
        """
        attachment = super(EmailHTML, self)._create_attachment(filename, content, mimetype)
        if filename and with_id:
            # change headers to suit
            del attachment["Content-Disposition"]
            mimetype = attachment["Content-Type"]
            del attachment["Content-Type"]
            attachment.add_header("Content-Type", mimetype, name=filename)
            attachment.add_header("Content-ID", "<%s>" % filename)
        return attachment
