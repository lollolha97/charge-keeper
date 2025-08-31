"""Setup script for A14 Charge Keeper GUI."""

from setuptools import setup, find_packages

setup(
    name="a14-charge-keeper-gui",
    version="0.1.0",
    description="Battery charge threshold manager GUI for Linux laptops",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "psutil>=5.8.0",
    ],
    entry_points={
        "console_scripts": [
            "a14-charge-keeper-gui=gui.system_tray:main",
        ],
    },
)