from distutils.core import setup

setup(name='rshiny_acl',
      version='1.0.0',
      description='HMDC utility to manage RShiny ACL in application directories.',
      url='https://github.com/hmdc/rshiny_acl',
      author='Evan Sarmiento',
      author_email='esarmien@g.harvard.edu',
      packages=['ShinyACL'],
      scripts=['scripts/rshiny_acl.py']
)
