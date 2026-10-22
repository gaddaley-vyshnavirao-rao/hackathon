from iaia.analyzers.source_code_analyzer import SourceCodeAnalyzer
def test_ast_findings(tmp_path):
 (tmp_path/'x.py').write_text('def f(x):\n return eval(x)\n')
 files,mods,findings=SourceCodeAnalyzer().analyze(tmp_path)
 assert mods[0].name=='x' and any(f.category=='code-execution' for f in findings)
