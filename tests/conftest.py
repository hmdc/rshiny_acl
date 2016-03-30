import pytest

@pytest.fixture(scope="module")
def shinyacl():
  from shinyacl import ShinyACL
  return ShinyACL
