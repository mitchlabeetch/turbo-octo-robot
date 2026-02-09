from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ma_advisory",
    version="1.0.0",
    description="M&A Advisory ERP - A derivative of ERPNext for mid-cap M&A advisory firms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Custom",
    author_email="contact@example.com",
    url="https://github.com/mitchlabeetch/turbo-octo-robot",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Frappe",
        "Topic :: Office/Business :: Financial",
    ],
)
