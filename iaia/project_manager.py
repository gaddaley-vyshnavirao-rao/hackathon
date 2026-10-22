from __future__ import annotations
import os, shutil, tempfile, zipfile
from pathlib import Path, PurePosixPath

class UnsafeArchiveError(ValueError): pass

class ProjectManager:
    def __init__(self, max_archive=25*1024*1024, max_files=2000, max_extracted=100*1024*1024):
        self.max_archive, self.max_files, self.max_extracted = max_archive, max_files, max_extracted
        self.ignored = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'node_modules', 'dist', 'build'}
    def _validate(self, z: zipfile.ZipFile):
        if len(z.infolist()) > self.max_files: raise UnsafeArchiveError('Too many archive entries')
        total = 0
        for i in z.infolist():
            p = PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or ':' in p.parts[0] if p.parts else False: raise UnsafeArchiveError('Unsafe archive path')
            if i.filename.startswith(('\\','/')) or (len(i.filename)>1 and i.filename[1]==':'): raise UnsafeArchiveError('Absolute archive path')
            mode = (i.external_attr >> 16) & 0o170000
            if mode and mode != 0o100000 and not i.is_dir(): raise UnsafeArchiveError('Links and special files are rejected')
            total += i.file_size
            if total > self.max_extracted: raise UnsafeArchiveError('Archive expands beyond limit')
    def extract(self, source, destination=None) -> Path:
        if hasattr(source, 'read'):
            data = source.read(self.max_archive + 1)
            if len(data) > self.max_archive: raise UnsafeArchiveError('Archive is too large')
            import io; z = zipfile.ZipFile(io.BytesIO(data))
        else:
            path = Path(source)
            if path.stat().st_size > self.max_archive: raise UnsafeArchiveError('Archive is too large')
            z = zipfile.ZipFile(path)
        self._validate(z)
        root = Path(destination or tempfile.mkdtemp(prefix='iaia-')).resolve()
        root.mkdir(parents=True, exist_ok=True)
        try:
            for item in z.infolist():
                parts = [p for p in PurePosixPath(item.filename).parts if p not in self.ignored]
                if not parts or any(p in self.ignored for p in parts): continue
                target = (root.joinpath(*parts)).resolve()
                if root not in target.parents and target != root: raise UnsafeArchiveError('Extraction escaped workspace')
                if item.is_dir(): target.mkdir(parents=True, exist_ok=True); continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(item) as src, target.open('xb') as dst: shutil.copyfileobj(src, dst)
        except Exception:
            shutil.rmtree(root, ignore_errors=True); raise
        return root
    def cleanup(self, root): shutil.rmtree(Path(root), ignore_errors=True)
    def files(self, root):
        return sorted(str(p.relative_to(root)) for p in Path(root).rglob('*') if p.is_file() and not any(x in self.ignored for x in p.parts))
