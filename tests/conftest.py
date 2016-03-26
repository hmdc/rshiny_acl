import pytest

@pytest.fixture(scope="module")
def shinyacl():
  from ShinyACL import ShinyACL
  return ShinyACL
