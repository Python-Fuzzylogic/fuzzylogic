from setuptools import setup, find_packages

setup(
    name='research_project',
    version='0.1.0',
    description='CHANGETHIS research project as Python module structure',
    long_description="<add a longer description>",
    author='Written by Ian Ozsvald',
    author_email='ian@ianozsvald.com',
    url='CHANGETHIS http:///',
    license='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],  #["numpy>=1.10"], # we use Anaconda instead of pip
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python']
)
