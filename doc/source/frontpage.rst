RShiny ACL
==========

What does it do?
----------------

``rshiny_acl`` allows you to add and remove user access to your rShiny
applications.

Usernames can be in the form of ``g.harvard.edu`` email addresses or HUID.

All the following commands must be run from the terminal.

Listing your available applications
-----------------------------------
::

  $ rshiny_acl --list-applications

  Project space: /nfs/www/shinyserver/myprojectspace
  --------------------------------------------------
  /nfs/www/shinyserver/myprojectspace/a
  /nfs/www/shinyserver/myprojectspace/b
  /nfs/www/shinyserver/myprojectspace/c

Adding a user
-------------
To add the user ``test@g.harvard.edu`` to application ``a``,
run::

  $ rshiny_acl --add-user /nfs/www/shinyserver/myprojectspace/a test@g.harvard.edu

To add multiple users, run::

  $ rshiny_acl --add-user /nfs/www/shinyserver/myprojectspace/a test@g.harvard.edu test2@g.harvard.edu test3@g.harvard.edu 88888888

Removing all users
------------------
To remove all users from an application ``a``,
run::

  $ rshiny_acl --del-all /nfs/www/shinyserver/myprojectspace/a

Removing a user
---------------
To remove the user ``test@g.harvard.edu`` from the application ``a``,
run::

  $ rshiny_acl --del-user /nfs/www/shinyserver/myprojectspace/a test@g.harvard.edu

To add multiple users, run::

  $ rshiny_acl --del-user /nfs/www/shinyserver/myprojectspace/a test@g.harvard.edu test2@g.harvard.edu test3@g.harvard.edu 88888888

Listing users
-------------
To list users which have access to the application ``a``, run::

  $ rshiny_acl --list-users /nfs/www/shinyserver/myprojectspace/a
