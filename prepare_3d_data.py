"""Generate offline 3D tests and optionally download Stanford Bunny (network required).

Usage:
    python prepare_3d_data.py
    python prepare_3d_data.py --download-bunny
"""
from pathlib import Path
import argparse
import sys
import tarfile
import tempfile
import urllib.request

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from three_d_data import ensure_procedural_datasets, load_ply_xyz, write_ply_ascii

STANFORD_URL='https://graphics.stanford.edu/pub/3Dscanrep/bunny.tar.gz'


def download_bunny(dest: Path) -> Path:
    """Download the Stanford repository archive; extract only bun_zipper.ply."""
    dest.mkdir(parents=True,exist_ok=True)
    target=dest/'bun_zipper.ply'
    if target.exists(): return target
    with tempfile.TemporaryDirectory() as tmp:
        archive=Path(tmp)/'bunny.tar.gz'
        urllib.request.urlretrieve(STANFORD_URL,archive)
        with tarfile.open(archive,'r:gz') as tf:
            matches=[x for x in tf if x.isfile() and x.name.endswith('/bun_zipper.ply')]
            if len(matches)!=1: raise RuntimeError('Archive did not contain bun_zipper.ply')
            member=matches[0]
            if member.size>50_000_000: raise RuntimeError('Unexpectedly large Bunny file')
            stream=tf.extractfile(member)
            if stream is None: raise RuntimeError('Could not read Bunny PLY')
            target.write_bytes(stream.read())
    p=load_ply_xyz(target)
    print(f'Downloaded {target} with {len(p)} vertices')
    return target


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--download-bunny',action='store_true',help='Download real Stanford Bunny PLY')
    args=parser.parse_args()
    data=ROOT/'data'/'3d'
    for path in ensure_procedural_datasets(data): print('Ready:',path.relative_to(ROOT))
    if args.download_bunny:
        try: download_bunny(data)
        except Exception as exc:
            print(f'Bunny download failed: {exc}',file=sys.stderr)
            print('If necessary, download bunny.tar.gz from the Stanford repository and copy bun_zipper.ply to data/3d/.',file=sys.stderr)
            raise SystemExit(1)

if __name__=='__main__': main()
