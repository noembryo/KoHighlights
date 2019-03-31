from distutils.core import setup

setup(name="KoHighlights", version="1.0.0.0", author="noEmbryo",
      packages=["future", "mechanize", "beautifulsoup4", "pyside"],
      url="https://github.com/noembryo/KoHighlights", license="MIT",
      author_email="noembryo@gmail.com",
      description=("A utility for viewing KoReader's highlights and/or "
                   "export them to simple text or html files."))
