import smtplib
fromMail = "nelsongomesneto15@gmail.com"

server = smtplib.SMTP('smtp.gmail.com', 587)
server.connect('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.ehlo()

server.login(fromMail, PASSWORDEXPOSED)

message = "\nHello!"

server.sendmail(fromMail, "ngomesneto@outlook.com", message)