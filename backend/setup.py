from setuptools import setup, find_packages

with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chathub-backend",
    version="1.0.0",
    author="ChatHub Team",
    author_email="contact@chathub.com",
    description="ChatHub AI API 集成平台后端服务",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaomengdashi/AI-ChatHub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask==3.0.0",
        "Flask-CORS==4.0.0",
        "Flask-SQLAlchemy==3.1.1",
        "SQLAlchemy==2.0.35",
        "Werkzeug==3.0.1",
        "openai==1.99.5",
        "requests==2.31.0",
        "PyJWT==2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "chathub-backend=app:main",
        ],
    },
    license="MIT",
    keywords="ai, api, chatbot, flask, openai, claude, gemini",
)