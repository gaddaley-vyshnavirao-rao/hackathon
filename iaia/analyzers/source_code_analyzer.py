from __future__ import annotations
import ast, re
from pathlib import Path
from iaia.models import Finding, ModuleInfo

class SourceCodeAnalyzer:
    def analyze(self, root: str):
        modules, findings, files = [], [], []
        for path in sorted(Path(root).rglob('*.py')):
            if any(x in {'.git','.venv','venv','__pycache__'} for x in path.parts): continue
            rel = str(path.relative_to(root)).replace('\\','/') ; files.append(rel)
            name = rel[:-3].replace('/','.')
            try: text = path.read_text(encoding='utf-8'); tree = ast.parse(text, filename=rel)
            except (SyntaxError, UnicodeDecodeError) as e:
                findings.append(Finding(title='File could not be parsed', category='quality', severity='medium', file_path=rel, evidence=str(e), explanation='Static analysis skipped this file.', confidence=.99, limitations='Syntax and encoding errors prevent AST analysis.')); continue
            imports=[]; classes=[]; funcs=[]
            for n in ast.walk(tree):
                if isinstance(n, ast.Import): imports += [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom): imports.append('.' * n.level + (n.module or ''))
                elif isinstance(n, ast.ClassDef): classes.append(n.name)
                elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): funcs.append(n.name)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {'eval','exec'}:
                    findings.append(Finding(title=f'Use of {n.func.id}()', category='code-execution', severity='high', file_path=rel, line=n.lineno, evidence=f'{n.func.id}(...)', explanation='Dynamic evaluation can execute unintended input.', confidence=.95, limitations='Static analysis cannot determine whether input is trusted.', recommendation='Replace dynamic evaluation with a constrained parser or explicit allowlisted dispatch.'))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in {'loads','load'} and isinstance(n.func.value, ast.Name) and n.func.value.id in {'pickle','yaml'}:
                    title='Unsafe pickle deserialization' if n.func.value.id == 'pickle' else 'Potential unsafe YAML deserialization'
                    findings.append(Finding(title=title, category='deserialization', severity='high', file_path=rel, line=n.lineno, evidence=f'{n.func.value.id}.{n.func.attr}(...)', explanation='Deserializers may execute or construct unsafe objects when input is untrusted.', confidence=.75, limitations='The input trust boundary is unknown.', recommendation='Use a safe schema-based format and validate untrusted input before deserialization.'))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'subprocess' and n.func.attr in {'run','call','Popen','check_call','check_output'}:
                    findings.append(Finding(title='Dangerous subprocess call', category='command-execution', severity='high', file_path=rel, line=n.lineno, evidence=f'subprocess.{n.func.attr}(...)', explanation='Process execution can enable command injection or unsafe process launch when arguments are influenced by untrusted input.', confidence=.82, limitations='Static analysis cannot determine input origin or runtime arguments.', recommendation='Use a validated argument list, avoid shell=True, and apply an allowlist for executable and arguments.'))
                if isinstance(n, ast.ExceptHandler) and n.type is None:
                    findings.append(Finding(title='Broad exception handler', category='quality', severity='low', file_path=rel, line=n.lineno, evidence='except:', explanation='Catching every exception can hide failures and complicate recovery.', confidence=.98, limitations='Some boundary code intentionally catches broad exceptions.'))
            for m in re.finditer(r'(?i)(password|passphrase|secret|api[_-]?key|token)\s*=\s*["\'][^"\']+["\']', text):
                key = m.group(1).lower().replace('-', '_')
                title = 'Hardcoded Password' if key in {'password', 'passphrase'} else 'Hardcoded API Key' if 'api' in key else 'Possible Hardcoded Secret'
                findings.append(Finding(title=title, category='secret-management', severity='high', file_path=rel, line=text[:m.start()].count('\n')+1, evidence=f'{m.group(1)} assigned a string literal', explanation='Credentials in source can be exposed through source control or artifacts.', confidence=.72, limitations='The value may be a test placeholder; rotate and validate manually.', recommendation='Remove the value from source, rotate confirmed credentials, and load secrets from a managed secret store.'))
            if len(text.splitlines()) > 500: findings.append(Finding(title='Unusually large module', category='architecture', severity='medium', file_path=rel, evidence=f'{len(text.splitlines())} lines', explanation='Large modules often mix responsibilities and increase change impact.', confidence=.9, limitations='Size alone does not prove poor design.'))
            modules.append(ModuleInfo(name=name, path=rel, classes=classes, functions=funcs, imports=imports, lines=len(text.splitlines()), complexity=sum(isinstance(n,(ast.If,ast.For,ast.While,ast.Try,ast.BoolOp)) for n in ast.walk(tree))))
        return files, modules, findings

