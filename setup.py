from setuptools import setup, find_packages
setup(
    name = 'spline-users',
    version = '0.1',
    packages = find_packages(),

    install_requires = ['spline'],

    include_package_data = True,

    zip_safe = False,

    entry_points = {'spline.plugins': 'users = splinext.users:UsersPlugin'},

    namespace_packages = ['splinext'],
)
