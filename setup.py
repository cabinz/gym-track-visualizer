from setuptools import setup, find_packages
import os

authors = [
    'Cabin Zhu',
]

if __name__ == '__main__':
    # Read the requirements from the requirements.txt file
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        requirements = f.read().splitlines()

    setup(
        name='gviz',
        version='1.0.0',
        description='Scripts for analyzing and visualizing your workout data.',
        author=', '.join(authors),
        author_email='cabin_zhu@foxmail.com',
        license='Apache 2.0',
        url='https://github.com/cabinz/gym-track-visualizer',
        package_dir={'': 'src'},
        packages=find_packages(
            where='src',
            exclude=['tests', 'tests.*']
        ),
        python_requires='>=3.8',
        install_requires=requirements,
    )
