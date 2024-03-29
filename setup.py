from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="anime_king_r",
    version='0.2.3',
    author='GhoulKingR',
    author_email='oduahchigozie46@gmail.com',
    description='An anime bot to download your favourite animes',
    url='https://github.com/GhoulKingR/AnimeKingR',
    scripts=['./scripts/akr-download'],
    packages=find_packages(),
    license='MIT',
    install_requires=[
        "requests == 2.31.0",
        "selenium == 4.16.0",
        "tqdm == 4.66.1",
        "setuptools == 68.1.2",
        "colorama==0.4.6",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
