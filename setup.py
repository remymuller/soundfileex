from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='SoundFileEx',
    version='0.1',
    description='An extended audio library based on libsndfile, CFFI and NumPy',
    url='https://bitbucket.org/remymuller/soundfileex',
    author='remy muller',
    author_email='r.muller@uvi.net',
    license='MIT',
    keywords=['audio', 'libsndfile'],
    packages=find_packages(),
    zip_safe=True,
    setup_requires=["PySoundFile>=0.9"],
    install_requires=['PySoundFile>=0.9'],
    test_suite='nose.collector',
    tests_require=['nose'],
    #    cffi_modules=["soundfile_build.py:ffibuilder"],
#    extras_require={'numpy': ['numpy']},
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Multimedia :: Sound/Audio',
    ],
#    long_description=open('README.rst').read(),
#    tests_require=['pytest'],
#    cmdclass=cmdclass,
)
