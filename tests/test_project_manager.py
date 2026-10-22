import io, zipfile, pytest
from iaia.project_manager import ProjectManager, UnsafeArchiveError
def z(data):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as q:q.writestr('x.py',data)
 b.seek(0); return b
def test_safe_extract(tmp_path): assert (ProjectManager().extract(z('x=1'),tmp_path/'out')/'x.py').read_text()=='x=1'
def test_traversal_rejected(tmp_path):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as q:q.writestr('../x.py','x')
 b.seek(0)
 with pytest.raises(UnsafeArchiveError): ProjectManager().extract(b,tmp_path/'out')
