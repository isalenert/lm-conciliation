from setuptools import setup, find_packages

setup(
    name="lm-conciliation",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pandas==2.1.3",
        "PyPDF2==3.0.1",
        "python-multipart==0.0.6",
        "fuzzywuzzy==0.18.0",
        "python-Levenshtein==0.23.0",
        "chardet==5.2.0",
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
    ],
)
