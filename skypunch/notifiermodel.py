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
NotifierModel class is an abstraction of the SQL notifiers database allows R/W operations to the SQL database.
"""
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker
from skypunchconfig import SkyPunchConfig

class Notifiers(object):
    pass

class NotifierModel:

    # setup logger, config and sqlalchemy session
    def __init__(self,logger,config):
        self.logger=logger
        self.config=config
        self.session=self.get_session()

    # create a session from config file settings
    def get_session(self):
        dbUri = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}'
        engine = create_engine(dbUri.format(user=self.config.getstr('database','user'),
                                            password=self.config.getstr('database','password'),
                                            host=self.config.getstr('database','location'),
                                            port=self.config.getint('database','port'),
                                            db=self.config.getstr('database','dbname')))
        metadata = MetaData(engine)
        notifiers = Table('notifiers',metadata,autoload=True)
        mapper(Notifiers,notifiers)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    # write the resources to the db
    def commit(self):
        self.session.commit()	

    # get a target based on its id
    def get(self,id):
        res = self.session.query(Notifiers).get(id)
        return res

    # get all the ids for the specified target
    def get_ids(self,target):
        res = self.session.query(Notifiers).all()
        ids = []
        for x in range(0,len(res)):
            ids.append(res[x].id)
        return ids 
