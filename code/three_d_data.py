"""3D point-cloud data loader and reproducible *procedural* benchmarks.

This file deliberately does not mislabel generated surfaces as scanned data.
Stanford's real bunny PLY can be placed in data/3d/; see README-data.txt.
Only NumPy is necessary to read these PLYs, including binary Stanford PLYs.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np

PLY_DTYPES = {
    'char': 'i1', 'int8': 'i1', 'uchar':'u1', 'uint8':'u1',
    'short':'i2', 'int16':'i2', 'ushort':'u2', 'uint16':'u2',
    'int':'i4', 'int32':'i4', 'uint':'u4', 'uint32':'u4',
    'float':'f4', 'float32':'f4', 'double':'f8', 'float64':'f8',
}


def load_ply_xyz(path: str | Path) -> np.ndarray:
    """Load x/y/z vertex coordinates from ASCII or binary PLY (little/big endian).

    Supports ordinary scalar vertex properties, even if other elements such as
    faces use list properties. Fails clearly for unsupported vertex lists.
    """
    path=Path(path)
    with path.open('rb') as f:
        if f.readline().strip() != b'ply':
            raise ValueError(f'Not a PLY file: {path}')
        fmt = None
        n_vertices = None
        props = []
        current = None
        while True:
            line=f.readline()
            if not line:
                raise ValueError('PLY header missing end_header')
            s=line.decode('ascii',errors='replace').strip().split()
            if not s: continue
            if s[0]=='format': fmt=s[1]
            elif s[0]=='element':
                current=s[1]
                if current=='vertex': n_vertices=int(s[2])
            elif s[0]=='property' and current=='vertex':
                if len(s)!=3 or s[1] not in PLY_DTYPES:
                    raise ValueError('Unsupported vertex PLY property')
                props.append((s[2],s[1]))
            elif s[0]=='end_header': break
        if n_vertices is None or fmt is None or not {'x','y','z'}.issubset({p[0] for p in props}):
            raise ValueError('PLY needs x/y/z vertex properties')
        if not (3<=n_vertices<=5_000_000):
            raise ValueError('Unexpected number of PLY vertices')
        if fmt=='ascii':
            coord_idx=[next(i for i,p in enumerate(props) if p[0]==a) for a in ('x','y','z')]
            values=np.empty((n_vertices,3), dtype=np.float64)
            for i in range(n_vertices):
                parts=f.readline().split()
                if len(parts)<len(props): raise ValueError('Truncated ASCII PLY')
                values[i]=[float(parts[j]) for j in coord_idx]
        elif fmt in ('binary_little_endian','binary_big_endian'):
            endian='<' if fmt=='binary_little_endian' else '>'
            dtype=np.dtype([(name,endian+PLY_DTYPES[typ]) for name,typ in props])
            table=np.fromfile(f, dtype=dtype,count=n_vertices)
            if len(table)!=n_vertices: raise ValueError('Truncated binary PLY')
            values=np.column_stack([table[a] for a in ('x','y','z')]).astype(float)
        else: raise ValueError(f'Unsupported PLY format: {fmt}')
    if not np.all(np.isfinite(values)): raise ValueError('PLY has NaN/Inf point coordinates')
    return values


def write_ply_ascii(path: str | Path, vertices: np.ndarray) -> None:
    """Store point locations as ASCII PLY; no triangle faces are invented."""
    points=np.asarray(vertices,dtype=float)
    if points.ndim!=2 or points.shape[1]!=3 or not np.all(np.isfinite(points)):
        raise ValueError('Expected finite (N,3) point cloud')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='ascii',newline='\n') as f:
        f.write(f'ply\nformat ascii 1.0\ncomment synthetic 3D point cloud\nelement vertex {len(points)}\n')
        f.write('property float x\nproperty float y\nproperty float z\nend_header\n')
        np.savetxt(f,points,fmt='%.9g')


def normalize_cloud(points: np.ndarray) -> np.ndarray:
    """Centre and divide by longest bounding box side, so 1 unit = object extent."""
    p=np.asarray(points,dtype=float)
    if p.ndim!=2 or p.shape[1]!=3 or len(p)<10:
        raise ValueError('Cloud must have at least 10 3D points')
    p=p-p.mean(axis=0)
    extent=float(np.ptp(p,axis=0).max())
    if extent<1e-12: raise ValueError('Degenerate 3D cloud')
    return p/extent


def generate_synthetic_surfaces(seed: int=2026, points: int=7000) -> dict[str,np.ndarray]:
    """Two non-planar, asymmetric benchmark surfaces (NOT real sensor scans)."""
    rng=np.random.default_rng(seed)
    u=rng.uniform(0,2*np.pi,points)
    z=rng.uniform(-1,1,points)
    phi=np.arccos(z)
    radial=(1+0.20*np.sin(3*u+0.4)*np.sin(phi)**2
            +0.12*np.cos(5*phi+u)*np.sin(phi)
            +0.14*np.exp(-((phi-1.1)**2+(u-1.0)**2)/0.25))
    lobe=np.column_stack([0.9*radial*np.sin(phi)*np.cos(u),
                          0.7*radial*np.sin(phi)*np.sin(u),
                          1.05*radial*np.cos(phi)+0.08*np.sin(2*u)*np.sin(phi)])

    t=rng.uniform(0,2*np.pi,points)
    v=rng.uniform(0,2*np.pi,points)
    major=0.8+0.13*np.sin(3*t)+0.07*np.cos(5*t+0.3)
    minor=0.23+0.045*np.cos(2*t+1)
    tube=np.column_stack([(major+minor*np.cos(v))*np.cos(t),
                          0.85*(major+minor*np.cos(v))*np.sin(t),
                          0.26*np.sin(t)+0.16*np.sin(2*t+0.4)+minor*np.sin(v)])
    return {'asymmetric_shell':normalize_cloud(lobe),
            'curved_tube':normalize_cloud(tube)}


def ensure_procedural_datasets(data_dir: str | Path) -> list[Path]:
    """Generate and save the same test clouds on any machine, offline."""
    data_dir=Path(data_dir)
    out=[]
    for name,points in generate_synthetic_surfaces().items():
        path=data_dir/f'{name}.ply'
        if not path.exists(): write_ply_ascii(path, points)
        out.append(path)
    return out
