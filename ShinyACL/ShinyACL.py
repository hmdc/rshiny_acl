import os
import re

NO_USERS_CONFIGURED = 1
USER_ALREADY_EXISTS = 2
DOTRSHINYCONF_TEMPLATE = "required_user {0};\n"

class ShinyACL:
  def __init__(self):
   self.__project_spaces__ = self.__get_shiny_project_spaces__()
   self.__apps__ = self.__build_shiny_app_tree__(self.__project_spaces__)
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
    with open('{0}/.shiny_app.conf'.format(app), 'r') as dotshinyconf:
      users = filter(lambda l: re.findall('^required_user.*;$', l), dotshinyconf.readlines())

      if len(users) == 0:
        return NO_USERS_CONFIGURED

      return users[0].rstrip()[:-1].split(' ')[1:]

  def add_user(self,app,username):
    if username in self.get_users(app):
      return USER_ALREADY_EXISTS
    else:
      return DOTRSHINYCONF_TEMPLATE.format(' '.join(self.get_users(app))
        + ' ' + username)

  def del_user(self,app,username):
    if username in self.get_users(app):
      return DOTRSHINYCONF_TEMPLATE.format(' '.join(filter(
        lambda u: u != username, self.get_users(app))))
    else: 
      return None

  def reload(self):
    return None
