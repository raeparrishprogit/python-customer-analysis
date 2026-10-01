"""Download original public data; extracted raw files are ignored by Git."""
from pathlib import Path
from urllib.request import urlopen
import shutil
import zipfile
import tempfile

ROOT = Path(__file__).resolve().parent
URL = 'https://archive.ics.uci.edu/static/public/352/online+retail.zip'
def main():
    target = ROOT / 'data/raw'
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() as archive:
        with urlopen(URL, timeout=120) as response:
            shutil.copyfileobj(response, archive)
        archive.seek(0)
        with zipfile.ZipFile(archive) as zipped:
            for name in zipped.namelist():
                if name.endswith(('.csv', '.xlsx')):
                    # Flatten filenames; archive paths cannot escape the raw directory.
                    (target / Path(name).name).write_bytes(zipped.read(name))
    print('Downloaded original data to', target)
if __name__ == '__main__':
    main()
