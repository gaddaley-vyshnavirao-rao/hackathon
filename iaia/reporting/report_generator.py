from __future__ import annotations
import html, json
from iaia.models import AnalysisResult
class ReportGenerator:
    def json(self, result: AnalysisResult): return result.model_dump_json(indent=2)
    def html(self, result: AnalysisResult):
        d=result.model_dump(); sections=[]
        for key in ('architecture','findings','blast_radius','recommendations','redesign','modernization'):
            sections.append(f'<h2>{html.escape(key.title())}</h2><pre>{html.escape(json.dumps(d.get(key), indent=2, default=str))}</pre>')
        return '<!doctype html><meta charset="utf-8"><title>IAIA report</title><h1>IAIA - '+html.escape(result.project_name)+'</h1>'+''.join(sections)
