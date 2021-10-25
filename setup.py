import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="subtitle-api",
    version="0.0.1",
    author="Erfan Shekari",
    author_email="erfan.dp.co@gmail.com",
    description="this module provide unofficial subscene.com api for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    python_requires=">=3.7",
    packages=["subtitle_api"],
    include_package_data=True,
    install_requires=[
        'beautifulsoup4==4.9.0',
        'requests==2.23.0',
        'IMDbPY==2021.4.18',
        'lxml==4.6.3',
    ],
)
