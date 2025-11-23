
from setuptools import setup, find_packages

setup(
    name="apex-eor-platform",
    version="1.0.0",
    author="Your Name",
    description="Scientific discovery platform for shale EOR",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "apex=apex.cli:main",
        ],
    },
)

