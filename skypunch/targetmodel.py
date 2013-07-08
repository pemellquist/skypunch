# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Peter Erik Mellquist pemellquist@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__docstring__ = """
TargetModel class is an abstraction of the SQL targets database allows R/W operations to the SQL targets database.
"""
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker
from skypunchconfig import SkyPunchConfig
import skypunchconfig

TABLENAME = 'targets'
STATUS_PASS = 'PASS'

class Targets(object):
    pass

# update target counters
def update_target_counters(target,response):
    if response != None:
        status = response.status
    else:
        status = 600
    if status >=200 and status < 300:
        target.count200 += 1
    elif status >= 300 and status < 400:
        target.count300 += 1
    elif status >= 400 and status < 500:
        target.count400 += 1
    elif status >= 500 and status < 600:
        target.count500 += 1
    else:
        target.network_fails += 1

# update target with new status, adjust previous status and bump counters
def update_target_status(target,status,description):
    target.previous_status = target.status
    target.status = status 
    target.status_description = description 
    if status == STATUS_PASS: 
        target.pass_count += 1
        target.repeated_fails = 0
    else:
        target.fail_count += 1
        target.repeated_fails += 1


class TargetModel:

    # setup logger, config and sqlalchemy session
    def __init__(self,logger,config):
        self.logger=logger
        self.config=config
        dbUri = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}'
        self.engine = create_engine(dbUri.format(user=self.config.getstr(skypunchconfig.DATABASE,skypunchconfig.USER),
                                        password=self.config.getstr(skypunchconfig.DATABASE,skypunchconfig.PASSWORD),
                                        host=self.config.getstr(skypunchconfig.DATABASE,skypunchconfig.LOCATION),
                                        port=self.config.getint(skypunchconfig.DATABASE,skypunchconfig.PORT),
                                        db=self.config.getstr(skypunchconfig.DATABASE,skypunchconfig.DBNAME)))

        metadata = MetaData(self.engine)
        targets = Table(TABLENAME,metadata,autoload=True)
        mapper(Targets,targets)
        self.session = self.get_session() 

    # create a session from config file settings
    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        self.session = session
        return session

    # close the session
    def close_session(self):
        self.session.close()

    # write the resources to the db
    def commit(self):
        self.session.commit()	

    # get a target based on its id
    def get(self,id):
        res = self.session.query(Targets).get(id)
        return res

    # get all the ids
    def get_ids(self):
        res = self.session.query(Targets).all()
        ids = []
        for x in range(0,len(res)):
            ids.append(res[x].id)
        return ids 
