from setuptools import setup

def read_reqs():
    reqs = [f.rstrip() for f in open('requirements.txt','r')]
    return reqs

setup(name='interactive_training',
      version='0.1',
      description='Interactive Robot Training',
      author='Ankit Shah',
      author_email='ajshah@mit.edu',
      license='MIT',
      packages=['interactive_training'],
      install_requires= read_reqs(),
      zip_safe=False)
