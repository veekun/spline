from setuptools import setup, find_packages
setup(
    name = 'spline-frontpage',
    version = '0.1',
    packages = find_packages(),

    install_requires = [
        'spline',
        'feedparser',
        'lxml',
    ],

    include_package_data = True,

    zip_safe = False,

    entry_points = {'spline.plugins': 'frontpage = splinext.frontpage:FrontPagePlugin'},

    namespace_packages = ['splinext'],
)
