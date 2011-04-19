<<<<<<< HEAD
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='spline',
    version='0.1',
    description='',
    author='',
    author_email='',
    #url='',
    install_requires=[
        "Pylons>=1.0",
        "SQLAlchemy>=0.6",
        "Mako>=0.3.4",
        "nose>=0.11",
        "WTForms>=0.6",
        'markdown',
        'lxml',
        'python-openid',
        'webhelpers>=1.2',
        # 'Babel>=0.9.5',  # needed for translation work only, can do without
    ],
    setup_requires=["PasteScript==dev,>=1.6.3dev-r7326"],
    packages=find_packages(exclude=['ez_setup']),

    include_package_data=True,
    package_data={'spline': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,

    test_suite='nose.collector',


    message_extractors = {'spline': [
        ('**.py', 'spline-python', None),
        ('**/templates/**.mako', 'spline-mako', {'input_encoding': 'utf-8'}),
        ('**/public/**', 'ignore', None)]},

    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = spline.config.middleware:make_app

    [paste.app_install]
    main = spline.installer:Installer

    [babel.extractors]
    spline-python = spline.babelplugin:extract_python
    spline-mako = spline.babelplugin:extract_mako

    [spline.plugins]
    users = splinext.users:UsersPlugin
    forum = splinext.forum:ForumPlugin
    """,
)
