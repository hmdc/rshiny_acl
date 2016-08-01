class ShinyACLUserAlreadyExists(Exception):
  def __init__(self, user, app):
    self.user = user
    self.app = app
  def __str__(self):
    return '{0} already has access to {1}'.format(self.user, self.app)

class ShinyACLNotAValidEmail(Exception):
   def __init__(self, user):
    self.user = user
   def __str__(self):
    return '{0} is not a valid e-mail address or HUID.'.format(self.user)
    
class ShinyACLUserDoesNotExist(Exception):
   def __init__(self, user, app):
     self.user = user
     self.app = app
   def __str__(self):
     return 'No such user {0} in access control list for app {1}'.format(self.user,self.app)

class ShinyACLNotAShinyApp(Exception):
   def __init__(self, appdir):
     self.appdir = appdir
   def __str__(self):
     return """\
Error
-----
   {0} is either not an RShiny application directory or is
   an RShiny application you do not have permission to access.
Troubleshooting
----------------
   Is there a server.R file present within this directory?
   Run the following command to list applications available to you:
      shiny_acl.py --list-applications
   Do you have the proper groups assigned to your username?
   For assistance, email rce_services@help.hmdc.harvard.edu""".format(self.appdir)
