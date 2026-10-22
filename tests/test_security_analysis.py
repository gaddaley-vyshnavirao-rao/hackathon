from iaia.analyzers.source_code_analyzer import SourceCodeAnalyzer


def test_security_indicators_include_recommendations(tmp_path):
    (tmp_path / 'security.py').write_text(
        "import pickle\nimport subprocess\nPASSWORD = 'demo'\nAPI_KEY = 'demo'\n"
        "def run(value):\n    eval(value)\n    exec(value)\n    pickle.loads(value)\n    return subprocess.run(value, shell=True)\n"
    )

    _, _, findings = SourceCodeAnalyzer().analyze(tmp_path)
    titles = {finding.title for finding in findings}

    assert 'Hardcoded Password' in titles
    assert 'Hardcoded API Key' in titles
    assert 'Use of eval()' in titles
    assert 'Use of exec()' in titles
    assert 'Unsafe pickle deserialization' in titles
    assert 'Dangerous subprocess call' in titles
    assert all(finding.recommendation for finding in findings if finding.category in {'code-execution', 'deserialization', 'command-execution', 'secret-management'})
