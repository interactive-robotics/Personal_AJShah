from setuptools import setup

def read_reqs():
    reqs = [f.rstrip() for f in open('requirements.txt','r')]
    return reqs

setup(name='meta_puns',
      version='0.1',
      description='meta and active learning with PUnS',
      author='Ankit Shah',
      author_email='ankit_j_shah@brown.edu',
      license='MIT',
      packages=['meta_puns'],
      install_requires= read_reqs(),
      zip_safe=False)
