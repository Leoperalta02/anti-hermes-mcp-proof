"""Deprecated Aura inbox sentinel.

This legacy Gmail/archive automation is intentionally disabled. It previously
contained trash, permanent-delete, attachment-offload, and token-writing paths.
Aura now uses only aura_safeguarded_tools.py.
"""


class AuraInboxSentinel:
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "Legacy AuraInboxSentinel is disabled; use apex_core.aura_safeguarded_tools"
        )


if __name__ == "__main__":
    raise SystemExit("Disabled: use the constrained Aura tools instead.")
