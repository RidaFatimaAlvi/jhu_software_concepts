"""Install configuration for the Module 5 Grad Cafe project."""

from setuptools import find_packages, setup


setup(
    name="gradcafe-module-5",
    version="0.1.0",
    description="Grad Cafe analytics Flask app with testing and security tooling.",
    packages=find_packages(include=["src", "src.*"]),
    include_package_data=True,
    package_data={"src": ["templates/*.html"]},
    install_requires=[
        "Flask>=2.3,<4",
        "psycopg[binary]>=3.0",
        "selenium>=4.0",
        "beautifulsoup4>=4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0,<9",
            "pytest-cov>=5.0,<7",
            "pylint>=4.0,<5",
            "pydeps>=3.0,<4",
            "Sphinx>=7.0,<9",
            "sphinx-rtd-theme>=2.0,<4",
        ]
    },
    python_requires=">=3.10",
)
