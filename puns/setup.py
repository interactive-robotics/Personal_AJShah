from setuptools import setup

def read_reqs():
    reqs = [f.rstrip() for f in open('requirements.txt','r')]
    return reqs

setup(name='puns',
      version='0.1',
      description='Planning with uncertain specifications',
      author='Ankit Shah',
      author_email='ajshah@mit.edu',
      license='MIT',
      packages=['puns'],
      install_requires= read_reqs(),
      zip_safe=False)
