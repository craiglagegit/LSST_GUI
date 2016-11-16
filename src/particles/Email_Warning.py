#!/usr/bin/env python
#Author: Craig Lage
#Date: 10-May-15
# These files contains various subroutines
# needed to run the LSST Simulator
# This code sends an E-Mail in the event of a failure

import sys, smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

#************************************* SUBROUTINES ***********************************************

def Send_Warning(message_subject, message_text):
    to_list=['cslage@ucdavis.edu', 'AndrewKBradshaw@gmail.com']
    msg = MIMEMultipart()
    msg['From']='ucdavislsst@gmail.com'
    msg['Subject']=message_subject
    msg.attach(MIMEText(message_text,'plain'))
    server=smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('ucdavislsst@gmail.com','Nerdlet14')
    for to_addr in to_list:
        msg['To']=to_addr
        text=msg.as_string()
        server.sendmail('ucdavislsst@gmail.com', to_addr, text)
    server.quit()
    return 

