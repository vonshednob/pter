import setuptools
import pathlib

try:
    import docutils.core
    from docutils.writers import manpage
except ImportError:
    docutils = None
    manpage = None

from pter import version


with open('README.md', encoding='utf-8') as fd:
    long_description = fd.read()


with open('LICENSE', encoding='utf-8') as fd:
    licensetext = fd.read()


def compile_documentation():
    htmlfiles = []

    if docutils is None:
        return htmlfiles

    dst = pathlib.Path('./pter/docs')
    dst.mkdir(exist_ok=True)
    
    pathlib.Path('./man').mkdir(exist_ok=True)

    man_pter = None

    if None not in [docutils, manpage]:
        for fn in pathlib.Path('./doc').iterdir():
            if fn.suffix == '.rst':
                if fn.stem == 'pter':
                    man_pter = str(fn)
                dstfn = str(dst / (fn.stem + '.html'))
                docutils.core.publish_file(source_path=str(fn),
                                           destination_path=dstfn,
                                           writer_name='html')
                htmlfiles.append('docs/' + fn.stem + '.html')

    if man_pter is not None:
        docutils.core.publish_file(source_path=man_pter,
                                   destination_path='man/pter.1',
                                   writer_name='manpage')

    return htmlfiles


def collect_icons():
    icons = []
    dst = pathlib.Path('./pter/icons')

    for fn in dst.iterdir():
        if fn.is_file() and fn.suffix == '.png':
            icons.append('icons/' + fn.name)

    return icons


setuptools.setup(
    name='pter',
    version=version.__version__,
    description="Console UI to manage your todo.txt file(s).",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/vonshednob/pter",
    author="R",
    author_email="devel+pter@kakaomilchkuh.de",
    entry_points={'console_scripts': ['pter=pter.main:run'],
                  'gui_scripts': ['qpter=pter.main:run']},
    packages=['pter'],
    package_data={'pter': collect_icons() + compile_documentation()},
    install_requires=['pytodotxt>=1.0.3'],
    extras_require={'xdg': ['pyxdg']},
    python_requires='>=3.0',
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console :: Curses',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3',])

