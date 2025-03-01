from setuptools import setup, find_packages
from src.AfdianBot.utils.constant import VERSION, AUTHOR, EMAIL

setup(
    name="AfdianBot",
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description="爱发电Bot SDK",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.32.2",
        "fake_useragent>=2.0.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)