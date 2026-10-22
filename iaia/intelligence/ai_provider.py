from __future__ import annotations
import os
class AIProvider:
    """Provider boundary; network calls are intentionally not implemented by default."""
    def available(self): return bool(os.getenv('IAIA_LLM_API_KEY'))
    def generate(self, payload, consent=False):
        if not consent: raise PermissionError('Explicit consent is required before external AI use')
        raise RuntimeError('No provider adapter configured; use deterministic mode')
