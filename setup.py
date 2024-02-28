import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / "VERSION").open() as f:
    version = f.read()
with (root_dir / "README.md").open() as f:
    long_description = f.read()
with (root_dir / "requirements.in").open() as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name="gn_module_dashboard",
    version=version,
    description="GeoNature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="Parcs nationaux des Écrins et des Cévennes",
    maintainer_email="geonature@ecrins-parcnational.fr",
    url="https://github.com/PnX-SI/gn_module_dashboard",
    packages=setuptools.find_packages("backend"),
    package_dir={"": "backend"},
    package_data={"gn_module_dashboard.migrations": ["data/*.sql"]},
    install_requires=requirements,
    tests_require=[
        "jsonschema",
    ],
    zip_safe=False,
    entry_points={
        "gn_module": [
            "code = gn_module_dashboard:MODULE_CODE",
            "picto = gn_module_dashboard:MODULE_PICTO",
            "blueprint = gn_module_dashboard.blueprint:blueprint",
            "config_schema = gn_module_dashboard.conf_schema_toml:GnModuleSchemaConf",
            "migrations = gn_module_dashboard:migrations",
            "tasks = gn_module_dashboard.tasks",
        ],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        "Operating System :: OS Independent",
    ],
)
