# SkyPunch Database schema
# pemellquist@gmail.com

USE skypunch;

INSERT INTO targets
VALUES (0,'Google home page','0','NEW',NULL,'NEW','','http://www.google.com','GET','NONE','',200,10,10,0,0,0,0,0,0,0,0,1);

INSERT INTO targets
VALUES (0,'Openstack Service','0','NEW',NULL,'','NEW','https://openstack.service.url','GET','OPENSTACK','user=xxxx,password=yyyyy,osauthendpoint=OPENSTACK_KEYSTONE_ENDPOINT,tenantid=ZZZZZZZZZZ',200,10,10,0,0,0,0,0,0,0,0,1);

INSERT INTO notifiers
VALUES(0, 'Peters gmail','SMTP','pemellquist@gmail.com','user=XXXXXXX,password=YYYYYYYY,server=smtp.gmail.com');
