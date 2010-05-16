from setuptools import setup, find_packages
setup(
    name = 'spline-forum',
    version = '0.1',
    packages = find_packages(),

    install_requires = [
        'spline',
        'spline-users',
    ],

    include_package_data = True,

    zip_safe = False,

    entry_points = {'spline.plugins': 'forum = splinext.forum:ForumPlugin'},

    namespace_packages = ['splinext'],
)
