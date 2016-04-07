import pytest
import os
from datetime import datetime

class TestShinyACLClass:
  def test_if_no_project_directory(self, shinyacl):
    "If bogus __root__ directory is defined, should []"

    assert shinyacl('/tmp').__get_shiny_project_spaces__('/tmp') == []

  def test_if_no_project_directory_subapps(self, shinyacl):
    "If bogus __root__ directory is defined, sub-apps should []"
    
    acl = shinyacl('/tmp')
    assert acl.__get_shiny_sub_apps__('/tmp') == []

  def test_if_project_space_in_list(self, shinyacl):
    "Using fixture, project space project should be in this list."
    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    assert 'project' in acl.__get_shiny_project_spaces__(acl.__root__)[0]

  def test_if_shiny_subapps_in_list(self, shinyacl):
    "Using fixture, check if subapps appear."
    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))
    assert 'app1' in acl.__get_shiny_sub_apps__(
                       acl.__get_shiny_project_spaces__(acl.__root__)[0])[0]
  
  def test_if_shiny_subapp_indexrmd_in_list(self, shinyacl):
    # Check if the app containing an index.Rmd shows up
    "Using fixture, check if subapps appear."
    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))
    assert 'app5' in acl.__get_shiny_sub_apps__(
                       acl.__get_shiny_project_spaces__(acl.__root__)[0])[-1]


  def test_build_shiny_app_tree(self, shinyacl):
    "Using fixture, check if tree is built properly."
    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))
    tree = acl.__build_shiny_app_tree__(
             acl.__get_shiny_project_spaces__(acl.__root__))

    assert 'project' in tree.keys()[0]
    assert 'app1' in tree.values()[0][0]

  def test_get_users_for_app_should_be_none(self, shinyacl):
    "App1 has no users defined."

    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    assert acl.get_users('{0}/fixtures/nfs/www/shinyserver/project/app1'.
             format(os.path.dirname(os.path.realpath(__file__)))) == []
           
  def test_get_users_for_directory_not_an_app(self, shinyacl):
    "This app should raise an exception that it's not an app."

    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    with pytest.raises(Exception):
      acl.get_users('app2_not_a_shiny_app')

  def test_get_users_for_app_has_two_users(self, shinyacl):

    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    assert acl.get_users('{0}/fixtures/nfs/www/shinyserver/project/app3'.
             format(os.path.dirname(os.path.realpath(__file__)))) == [
               'a@a.com', 'b@b.com']

  def test_add_user_not_valid_email(self, shinyacl):

    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    with pytest.raises(Exception):
      acl.add_user('app', ['notvalidemail'])

  def test_add_user_email_already_exist(self, shinyacl):
    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    with pytest.raises(Exception):
      acl.add_user('{0}/fixtures/nfs/www/shinyserver/project/app3'.
                     format(os.path.dirname(os.path.realpath(__file__))),
                   'a@a.com')

  def test_add_user_email(self, shinyacl):
    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    app = '{0}/fixtures/nfs/www/shinyserver/project/app4'.format(
            os.path.dirname(os.path.realpath(__file__)))

    acl.add_user(app, ['a@a.com'])

    assert acl.get_users(app) == ['a@a.com']

  
  def test_del_user_email(self, shinyacl):

    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    app = '{0}/fixtures/nfs/www/shinyserver/project/app4'.format(
            os.path.dirname(os.path.realpath(__file__)))

    acl.del_user(app, ['a@a.com'])

    assert acl.get_users(app) == []

  def test_reload(self, shinyacl):
  
    acl = shinyacl("{0}/fixtures/shared_space".format(
                     os.path.dirname(os.path.realpath(__file__))))

    app = '{0}/fixtures/nfs/www/shinyserver/project/app4'.format(
            os.path.dirname(os.path.realpath(__file__)))

    restart_txt = '{0}/restart.txt'.format(app)

    now = datetime.now()

    acl.reload(app)

    assert os.path.isfile(restart_txt)

    mtime_restart = \
    datetime.fromtimestamp(os.path.getmtime(restart_txt))

    # Make sure timestamp was updated.
    assert mtime_restart > now

