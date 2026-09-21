import logfire
from llm_guard.input_scanners import PromptInjection, Anonymize
from llm_guard.vault import Vault

# Initialize Logfire
logfire.configure()

class GuardrailsManager:
    def __init__(self):
        logfire.info("Initializing LLM-Guard Security Scanners...")
        
        # 1. Prompt Injection Scanner (Member 1)
        # Uses a local HuggingFace model to detect jailbreaks and injections
        self.injection_scanner = PromptInjection(threshold=0.5)
        
        # 2. PII / Anonymize Scanner (Member 2)
        # Detects sensitive data like emails, credit cards, names, and phone numbers
        self.vault = Vault()
        self.pii_scanner = Anonymize(vault=self.vault)
        
        logfire.info("Security Scanners initialized successfully.")

    def scan_for_injection(self, prompt: str) -> tuple[bool, float]:
        """
        Scans a prompt for injection attacks.
        Returns (is_safe, risk_score). We will default risk_score to 0.0 since it was removed.
        """
        with logfire.span("LLM-Guard: Scanning for Prompt Injection"):
            sanitized_prompt, is_safe = self.injection_scanner.scan(prompt)
            # LLM-Guard removed risk_score in the newer versions, so we default it to 0.0
            return is_safe, 0.0

    def scan_and_anonymize_pii(self, prompt: str) -> tuple[str, bool]:
        """
        Scans a prompt for PII and masks it (e.g., John -> [PERSON]).
        Returns (anonymized_prompt, is_safe).
        """
        with logfire.span("LLM-Guard: Scanning for PII"):
            anonymized_prompt, is_safe = self.pii_scanner.scan(prompt)
            return anonymized_prompt, is_safe

# Create a single global instance so the models are only loaded into memory once
guardrails = GuardrailsManager()
