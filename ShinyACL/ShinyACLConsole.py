from ShinyACL import ShinyACL
from .ShinyACLExceptions import ShinyACLUserAlreadyExists, \
ShinyACLUserDoesNotExist, \
ShinyACLNotAShinyApp, \
ShinyACLNotAValidEmail
from argparse import ArgumentParser

class ShinyACLConsole:
  def __init__(self):
    self.acl = ShinyACL()

  def list_applications(self):
    for key, value in self.acl.__apps__.iteritems():
      print """\
Project space: {0}
{1}
{2}""".format(key,
              '-' * len('Project space: {0}'.format(key)),
              '\n'.join(value))

    return None

  def list_users_for_application(self, app):
    print """\
{0}
{1}
{2}""".format(app, '-'*len(app), 
  (lambda users: "No users currently configured.\n" if users == [] else '\n'.join(users))(
    self.acl.get_users(app)))

  def del_user(self, app, user):
    return self.acl.del_user(app, user)

  def run(self):
    parser = ArgumentParser(
      description='Manage RShiny server access control lists'
    )

    group = \
    parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--list-applications', action='store_true',
      help='Lists rShiny applications available for you.')

    group.add_argument('--list-users',
      type=str,
      help='Lists users who have access to a specified application',
      default=None)

    group.add_argument('--add-user',
     type=str,
     nargs=2,
     help='Adds permission for a user defined by an Google e-mail\
address to access a specified application.')

    group.add_argument('--del-user',
     type=str,
     nargs=2,
     help='Removes permission for a user defined by a Google e-mail\
address to access a specified application.')

    args = parser.parse_args()

    if args.list_applications:
      self.list_applications()
    elif args.list_users:
      try:
        self.list_users_for_application(args.list_users)
      except ShinyACLNotAShinyApp as e:
        print e
      except IOError as e:
        print "No such application {0} available or permission\
 denied\n{1}".format(args.list_users, e)
    elif args.add_user:
      try:
        print self.acl.add_user(*args.add_user)
      except ShinyACLNotAValidEmail as e:
        print e 
      except IOError as e:
        print e
    elif args.del_user:
      try:
        print self.acl.del_user(*args.del_user)
      except IOError as e:
        print e

    return 0

      
