import os
import re
import subprocess
import logging
import logging.handlers
import pwd
from .ShinyACLExceptions import ShinyACLUserAlreadyExists, \
ShinyACLUserDoesNotExist, \
ShinyACLNotAShinyApp, \
ShinyACLNotAValidEmail

DOTRSHINYCONF_TEMPLATE = "required_user {0};\n"

class ShinyACL:
  def __init__(self,
   __root__ = '{0}/shared_space'.format(os.path.expanduser('~'))):

   self.__root__ = __root__
   self.__project_spaces__ = self.__get_shiny_project_spaces__(self.__root__)
   self.__apps__ = self.__build_shiny_app_tree__(self.__project_spaces__)
   self.log = logging.getLogger(__name__)
   self.log.setLevel(logging.CRITICAL)

   handler = logging.handlers.SysLogHandler(address = '/dev/log')
   logging.Formatter('%(module)s.%(funcName)s: %(message)s')
   handler.setFormatter(logging.Formatter('%(module)s.%(funcName)s: %(message)s'))

   self.log.addHandler(handler)
   return None

  def __get_shiny_project_spaces__(self, __root__):
   return filter(lambda t: 'shinyserver' in t.split('/'),
    map(lambda d: os.path.realpath(os.path.join(__root__, d)),
      os.listdir(__root__)))

  def __build_shiny_app_tree__(self, projectspaces):
    __tree__ = {}
    for projectspace in projectspaces:
      __tree__[projectspace] = \
        self.__get_shiny_sub_apps__(projectspace)
    return __tree__

  def __get_shiny_sub_apps__(self,projectspace):
    return filter(lambda d: os.path.isfile('{0}/server.R'.format(d)),
        filter(os.path.isdir, 
          map(lambda d: os.path.join(projectspace, d),
            os.listdir(projectspace))))
  
  def __get_project_space_name__(self,path):
    return path.split('/')[-1]

  def get_users(self,app):

    if filter(lambda (k,v): app in v, self.__apps__.iteritems()) == []:
      raise ShinyACLNotAShinyApp(app)

    try:
      with open('{0}/.shiny_app.conf'.format(app), 'r') as dotshinyconf:
        users = filter(lambda l: re.findall('^required_user.*;$', l), dotshinyconf.readlines())

        if len(users) == 0:
          return []

        return filter(lambda u: u != '', users[0].rstrip()[:-1].split(' ')[1:])
    except IOError as e:
      return []

  def __write__(self, app, authstring):
    with open('{0}/.shiny_app.conf'.format(app), 'w+') as dotshinyconf:
      data = dotshinyconf.readlines()
      line = filter(lambda index: index >= 0, map(lambda line: None if re.findall('^required_user.*;$', line) == [] else dotshinyconf.index(line), data))

      assert len(line) <= 1

      # There is no such line in the file
      if line == []:
        dotshinyconf.write(authstring);
      else: 
        data[line[0]] = authstring
        data.writelines(data)
      
    return None

  def add_user(self,app,usernames):
    email_regex = re.compile(
      "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    for username in usernames:
      if email_regex.findall(username) == []:
        raise ShinyACLNotAValidEmail(username)
      elif username in self.get_users(app):
        raise ShinyACLUserAlreadyExists(username, app)
      else:
        executing_user = pwd.getpwuid(os.getuid())[0]
        self.log.critical("{0} added user {1} to {2}".format(executing_user,
          username,
          app))
        self.__write__(app, DOTRSHINYCONF_TEMPLATE.format(' '.join(self.get_users(app))
          + ' ' + username.strip()))

    return None

  def del_user(self,app,usernames):

    for username in usernames:
      if username in self.get_users(app):
        executing_user = pwd.getpwuid(os.getuid())[0]
        self.log.critical("{0} removed user {1} from {2}".format(
          executing_user,
          username,
          app))
        self.__write__(app, DOTRSHINYCONF_TEMPLATE.format(' '.join(filter(
          lambda u: u != username, self.get_users(app)))))
      else: 
        raise ShinyACLUserDoesNotExist(username, app)

    return None

  def reload(self,app):
    with open('{0}/restart.txt'.format(app), 'a+') as restart_txt:
      os.utime('{0}/restart.txt'.format(app), None)
    return None    
