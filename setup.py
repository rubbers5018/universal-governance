#!/usr/bin/env python3
"""Setup script for Universal Governance."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="universal-governance",
    version="2.11.0",
    author="The_Nurse",
    author_email="dropstart01@pm.me",
    description="Cryptographic identity verification for distributed governance systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rbeachg941/universal-governance",
    project_urls={
        "Bug Reports": "https://github.com/rbeachg941/universal-governance/issues",
        "Source": "https://github.com/rbeachg941/universal-governance",
        "Documentation": "https://github.com/rbeachg941/universal-governance/blob/main/docs/",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-gnupg>=0.5.0",
        "ecdsa>=0.18.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "bandit>=1.7.0",
            "pip-audit>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "governance=mainscript:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
