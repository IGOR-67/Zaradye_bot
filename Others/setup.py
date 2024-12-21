from setuptools import setup, find_packages

setup(
    name='zaryadye_bot',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==21.6',
        'pandas==2.0.3',
        'gTTS==2.5.4',
        'fuzzywuzzy==0.18.0',
        'requests==2.32.3',
        'bing-image-downloader==1.1.2',
        # Добавьте другие зависимости из requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'zaryadye-bot=bot:main',  # Убедитесь, что у вас есть функция main() в bot.py
        ],
    },
)