"""
The ShinyACL module provides functionality to add and remove users from
.shiny.conf files inside Shiny application directires. The ShinyACL
module also handles application restarts via restart.txt when ACLs for
an application has changed
"""

__author__ = "Evan Sarmiento"
__email__ = "esarmien@g.harvard.edu"

import os
import re
import subprocess
import logging
import logging.handlers
import pwd
from shinyacl import ShinyACLUserAlreadyExists, \
ShinyACLUserDoesNotExist, \
ShinyACLNotAShinyApp, \
ShinyACLNotAValidEmail

DOTRSHINYCONF_TEMPLATE = "required_user {0};\n"

class ShinyACL:
  """The ShinyACL class provides methods which add, remove users to an 
  application's ACL in .shiny.conf and restarts that application.
  """

  def __init__(self,
   __root__ = '{0}/shared_space'.format(os.path.expanduser('~'))):
   """ShinyACL class initialization method.

   :param __root__: Optional, specifies where to look for shared_space
                    directories
   :type __root__: ``str``
   
   :Example:

   >>> from shinyacl import ShinyACL
   >>> acl = ShinyACL()

   :Example:

   >>> from shinyacl import ShinyACL
   >>> acl = ShinyACL('/some/other/path')
   """

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
   """Returns an array of project spaces in ``__root__`` directory.
   Determines if this is a shinyserver project space by looking at
   the full path of the symlink, if it includes shinyserver.

   :param __root__: Location of shared_space project directories
   :type __root__: ``str``
   :rtype: ``list``

   :Example:

   >>> from shinyacl import ShinyACL
   >>> ShinyACL().__get_shiny_project_spaces__('/nfs/home/E/esarmien/shared_space')
   ['/nfs/www/shinyserver/vpal']

   """

   return filter(lambda t: 'shinyserver' in t.split('/'),
    map(lambda d: os.path.realpath(os.path.join(__root__, d)),
      os.listdir(__root__)))

  def __build_shiny_app_tree__(self, projectspaces):
    """Builds a hash mapping of project directories to apps in those
    project directories.

    :param projectspaces: An array of project spaces, usually this is
                          the resultant list from
                          ``__get_shiny_project_spaces__``
    :type projectspaces: ``list``
    :rtype: ``dict``
   
    :Example:

    >>> from shinyacl import ShinyACL
    >>> acl = ShinyACL()
    >>> acl.__build_shiny_app_tree(acl.__get_shiny_project_spaces__('/nfs/home/E/esarmien/shared_space'))
    {'/nfs/www/shinyserver/vpal': ['/nfs/www/shinyserver/vpal/test_irt',
    '/nfs/www/shinyserver/vpal/irt_working',
    '/nfs/www/shinyserver/vpal/hello',
    '/nfs/www/shinyserver/vpal/courseviz',
    '/nfs/www/shinyserver/vpal/hello_protected']}

    """ 
     
    __tree__ = {}
    for projectspace in projectspaces:
      __tree__[projectspace] = \
        self.__get_shiny_sub_apps__(projectspace)
    return __tree__

  def __get_shiny_sub_apps__(self,projectspace):
    """Returns a list of apps belonging to an rShiny project space. A
    directory is determined to be an rShiny app if it has a ``server.R``
    or ``index.Rmd`` in it. 

    :param projectspace: Fully qualified path to project space
    :type projectspace: ``str``
    :rtype: ``list``

    :Example:
    
    >>> from shinyacl import ShinyACL
    >>> ShinyACL().__get_shiny_sub_apps('/nfs/www/shinyserver/vpal')
    ['/nfs/www/shinyserver/vpal/test_irt',
    '/nfs/www/shinyserver/vpal/irt_working',
    ...
    ]

    """

    return filter(lambda d: os.path.isfile('{0}/server.R'.format(d)) or os.path.isfile('{0}/index.Rmd'.format(d)), 
        filter(os.path.isdir, 
          map(lambda d: os.path.join(projectspace, d),
            os.listdir(projectspace))))
 
  # UNUSED function commented out. 
  # def __get_project_space_name__(self,path):
  #  return path.split('/')[-1]

  def get_users(self,app):
    """Returns a list of users which are allowed to access an application.
    Raises exception if the ``app`` argument is a path which is not a
    RShiny application. Returns an empty array if no users or configured
    or if ``.shiny_app.conf`` does not exist in the app directory.

    :param app: Fully qualified path to application directory
    :type app: ``str``
    :rtype: ``list``
    :raises:
      :py:exc:`shinyacl.ShinyACLExceptions.ShinyACLNotAShinyApp`
    
    :Example:

    >>> from shinyacl import ShinyACL
    >>> ShinyACL().get_users('/nfs/www/shinyserver/vpal/hello')
    ['dtingley@g.harvard.edu', 'v@v.com']

    """   

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
    """Writes the ``.shiny_app.conf`` file inside the app directory by
       modifying the required_user line. No need to use this as higher
       level methods like ``add_user`` call this function with the
       proper arguments.

    :param app: Fully qualified path to application directory
    :type app: ``str``
    :param authstring: The authentication line to write
    :type authstring: ``str``
   
    :Example:
    
    >>> from shinyacl import ShinyACL
    >>> ShinyACL().write('/nfs/www/shinyserver/vpal/hello',
          'required_user esarmien@g.harvard.edu;')

    """
    
      
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
    """Adds usernames to ``.shiny_app.conf`` for the specified app.
    Logs action to syslog per HEISP.

    :param app: Fully qualified path to application directory
    :type app: ``str``
    :param usernames: Array of usernames to add
    :type usernames: ``list``
    :retval: ``None``
    :rtype: ``None``
    :raises:
      :py:exc:`shinyacl.ShinyACLExceptions.ShinyACLNotAValidEmail`
    :raises:
      :py:exc:`shinyacl.ShinyACLExceptions.ShinyACLUserAlreadyExists`

    :Example:

    >>> from shinyacl import ShinyACL
    >>> ShinyACL().add_user('/nfs/www/shinyserver/vpal/hello',
          'esarmien@g.harvard.edu')

    """

    email_regex = re.compile(
      "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    huid_regex = re.compile(
      "^[0-9]{8}$"
    )

    for username in usernames:
      if email_regex.findall(username) == [] and huid_regex.findall(username) == []:
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

  def del_all(self, app):
    """Removes all usernames from ``.shiny_app.conf`` for specified app.
    Logs action to syslog per HEISP.

    :param app: Fully qualified path to application directory
    
    :Example:

    >>> from shinyacl import ShinyACL
    >>> ShinyACL().del_all('/nfs/www/shinyserver/vpal/hello')
    """

    executing_user = pwd.getpwuid(os.getuid())[0]
    self.__write__(app, DOTRSHINYCONF_TEMPLATE.format(''))
    self.log.critical("{0} removed all users from {1}".format(
      executing_user, app))

    return None

  def del_user(self,app,usernames):
    """Removes usernames from ``.shiny_app.conf`` for specified app.
    Logs action to syslog per HEISP.
    
    :param app: Fully qualified path to application directory
    :type app: ``str``
    :param usernames: Array of usernames to add
    :type usernames: ``list``
    :retval: ``None``
    :rtype: ``None``
    :raises:
      :py:exc:`shinyacl.ShinyACLExceptions.ShinyACLUserDoesNotExist`

    :Example:

    >>> from shinyacl import ShinyACL
    >>> ShinyACL().del_user('/nfs/www/shinyserver/vpal/hello',
          'esarmien@g.harvard.edu')

    """

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
    """Restarts an application by touching a ``restart.txt`` file in the
    application path and changing it's mtime.

    :param app: Fully qualified path to application directory
    :type app: ``str``
    :retval: ``None``
    :rtype: ``None``

    :Example:

    >>> from shinyacl import ShinyACL
    >>> ShinyACL().reload('/nfs/www/shinyserver/vpal/hello')
   
    """
 
    with open('{0}/restart.txt'.format(app), 'a+') as restart_txt:
      os.utime('{0}/restart.txt'.format(app), None)
    return None    
