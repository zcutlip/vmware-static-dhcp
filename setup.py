from setuptools import setup
about = {}
with open("vmware_static_dhcp/__about__.py") as fp:
    exec(fp.read(), about)

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(name=about["__title__"],
      version=about["__version__"],
      description=about["__summary__"],
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Zachary Cutlip",
      author_email="",
      url="TBD",
      license="MIT",
      packages=['vmware_static_dhcp'],
      entry_points={
          'console_scripts': ['vmwarestatic=vmware_static_dhcp.cli:main'], },
      python_requires='>=3.7',
      install_requires=['configure-with-sudo>=0.1.0.dev4'],
      package_data={'vmware_static_dhcp': ['config/*']},
      )
