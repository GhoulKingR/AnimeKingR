from setuptools import setup

setup(
    name="Anime bot",
    version='0.0.1',
    author='GhoulKingR',
    author_email='oduahchigozie46@gmail.com',
    description='An anime bot to download your favourite animes',
    url='https://github.com/GhoulKingR/anime-bot',
    scripts=['./scripts/anime-bot'],
    packages=['anime-bot'],
    license='MIT',
    install_requires=[
        "requests == 2.31.0",
        "selenium == 4.16.0",
        "tqdm == 4.66.1",
        "setuptools",
    ],
)