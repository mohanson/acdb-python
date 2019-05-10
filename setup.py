import os.path
import setuptools

root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='acdb',
    version='3.7.3',
    url='https://github.com/pydump/acdb',
    license='MIT',
    author='mohanson',
    author_email='mohanson@outlook.com',
    description='Package acdb manages objects between memory and file system.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['acdb']
)
