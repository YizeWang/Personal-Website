"""Copy the public site into _site; keep source data and local work private."""

from pathlib import Path
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / '_site'
PUBLIC_FILES = (
    'index.html',
    'education.html',
    'research.html',
    'publication--honors.html',
    'personal.html',
    'favicon.ico',
    '.nojekyll',
)
PUBLIC_DIRECTORIES = ('css', 'js', 'images')


def main():
    revision = os.environ.get('GITHUB_SHA') or subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True
    ).strip()
    # Recreate only this fixed build directory, so stale files cannot be published.
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir()
    for name in PUBLIC_FILES:
        shutil.copy2(ROOT / name, DESTINATION / name)
    for name in PUBLIC_DIRECTORIES:
        shutil.copytree(
            ROOT / name, DESTINATION / name,
            ignore=shutil.ignore_patterns('.DS_Store', '__pycache__', '*.pyc'),
        )
    (DESTINATION / 'revision.txt').write_text(revision + '\n', encoding='utf-8')
    print('Prepared public files in _site/.')


if __name__ == '__main__':
    main()
