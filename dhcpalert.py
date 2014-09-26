#!/usr/bin/python

# author: Michael Akey
# Simple script to one-shot email someone if a dhcp pool hits a certain threshold
#
# Pipe in the output of dhcpd-pools:
# dhcpd-pools -c dhcpd.conf -l dhcpd.leases -L 22 -f c | ./dhcpalert.py
import sys
import smtplib
from email.mime.text import MIMEText


# might want to configure this stuff!
ALERT_PERCENT = 95
RESET_PERCENT = 70
status_file = '.dhcpalert'
monitored_pools = ['Network1','Network2']
msg_from = 'dhcp@localhost'
email_to_alert = 'your.email@localhost'
smtp_server = 'localhost'
# end config

alerted_pools = []

#open status file, read lines - add each to a list, if available
f = open(status_file,'r')
for line in f.readlines():
    alerted_pools.append(line.replace('\n',''))
f.close()

for line in sys.stdin.readlines():
    data = line.replace('"','').split(',')
    try:
        # are we monitoring this pool?
        if data[0] in monitored_pools:
            # have we already alerted on it?
            if data[0] in alerted_pools:
                # are we below the reset threshold?
                if float(data[3]) < RESET_PERCENT:
                    alerted_pools.remove(data[0])
            else:
                # should we alert?
                if float(data[3]) > ALERT_PERCENT:
                    msg = MIMEText("%s pool usage at %s percent!" % (data[0],data[3]))
                    msg['Subject'] = "WARNING: %s pool utilization over threshold!" % data[0]
                    msg['To'] = email_to_alert
                    msg['From'] = msg_from
                    s = smtplib.SMTP(smtp_server)
                    s.sendmail(msg_from, [email_to_alert],msg.as_string())
                    s.quit()
                    alerted_pools.append(data[0])
    except:
        continue

# write new status file
f = open(status_file,'w')
for pool in alerted_pools:
    f.write(pool+'\n')
f.close()
