from __future__ import annotations
import json
from pathlib import Path
from iaia.models import AnalysisResult
class AnalysisRepository:
    def __init__(self, directory='.iaia-data'): self.directory=Path(directory); self.directory.mkdir(parents=True, exist_ok=True)
    def save(self, result):
        p=self.directory/(result.analysis_id+'.json'); p.write_text(result.model_dump_json(indent=2), encoding='utf-8'); return p
    def load(self, analysis_id):
        try: return AnalysisResult.model_validate_json((self.directory/(analysis_id+'.json')).read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError, ValueError): return None
