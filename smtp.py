# -*- coding: utf-8 -*-

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os

def sendMail(toAddresses, fromAddress, mailSubject, mailBodyHtml, server = "localhost"):
	# define mail's metadata
	oMessage = MIMEMultipart()
	oMessage['To'] = COMMASPACE.join(toAddresses)
	oMessage['From'] = fromAddress
	oMessage['Date'] = formatdate(localtime=True)
	oMessage['Subject'] = mailSubject
	
	# set mail body
	oMessage.attach(MIMEText(mailBodyHtml, 'html'))

	# send mail
	smtp = smtplib.SMTP(server)
	smtp.sendmail(fromAddress, toAddresses, oMessage.as_string() )
	smtp.close()
