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
  def __init__(self):
   self.__project_spaces__ = self.__get_shiny_project_spaces__()
   self.__apps__ = self.__build_shiny_app_tree__(self.__project_spaces__)
   self.log = logging.getLogger(__name__)
   self.log.setLevel(logging.CRITICAL)

   handler = logging.handlers.SysLogHandler(address = '/dev/log')
   logging.Formatter('%(module)s.%(funcName)s: %(message)s')
   handler.setFormatter(logging.Formatter('%(module)s.%(funcName)s: %(message)s'))

   self.log.addHandler(handler)
   return None

  def __get_shiny_project_spaces__(self):
   __root__ = '{0}/shared_space'.format(os.path.expanduser('~'))
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

        return users[0].rstrip()[:-1].split(' ')[1:]
    except IOError as e:
      return []

  def add_user(self,app,username):
    email_regex = re.compile(
      "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    if email_regex.findall(username) == []:
      raise ShinyACLNotAValidEmail(username)
    elif username in self.get_users(app):
      raise ShinyACLUserAlreadyExists(username, app)
    else:
      executing_user = pwd.getpwuid(os.getuid())[0]
      self.log.critical("{0} added user {1} to {2}".format(executing_user,
        username,
        app))
      return DOTRSHINYCONF_TEMPLATE.format(' '.join(self.get_users(app))
        + ' ' + username)

  def del_user(self,app,username):
    if username in self.get_users(app):
      executing_user = pwd.getpwuid(os.getuid())[0]
      self.log.critical("{0} removed user {1} from {2}".format(
        executing_user,
        username,
        app))
      return DOTRSHINYCONF_TEMPLATE.format(' '.join(filter(
        lambda u: u != username, self.get_users(app))))
    else: 
      raise ShinyACLUserDoesNotExist(username, app)

  def reload(self):
    return subprocess.call(["/usr/bin/sudo", "/sbin/reload", "shiny-server"])
