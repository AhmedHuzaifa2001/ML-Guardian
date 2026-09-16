import sys
from pathlib import Path

# Add backend directory to path so we can run this file directly
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import logfire
from security.guardrails import guardrails

class PIIDetector:
    def sanitize_input(self, user_input: str) -> str:
        """
        Uses NLP and LLM-Guard to detect and mask PII (Personally Identifiable Information) 
        like Names, Emails, Phone Numbers, and Credit Cards.
        Returns the sanitized string.
        """
        logfire.info("Sending prompt to LLM-Guard for PII anonymization...")
        
        # anonymized_text masks PII, e.g., "John" -> "[PERSON]"
        anonymized_text, is_safe = guardrails.scan_and_anonymize_pii(user_input)
        
        if not is_safe or anonymized_text != user_input:
            logfire.info(f"PII Detected and Masked. Original length: {len(user_input)}, New length: {len(anonymized_text)}")
        else:
            logfire.info("No PII detected in input.")
            
        return anonymized_text

# Create a single instance
pii_detector = PIIDetector()

if __name__ == "__main__":
    # Configure Logfire so it doesn't throw a warning when testing directly
    logfire.configure()
    
    # Test it directly
    test_safe = "I have a dataset with 500 rows about housing prices."
    test_leak = "My boss Alice Smith asked me to analyze this. Her email is alice.smith@megacorp.com and her phone is 555-0198."
    
    print("Testing Safe Input:")
    print("Original:", test_safe)
    print("Sanitized:", pii_detector.sanitize_input(test_safe))
    print("-" * 50)
    
    print("Testing PII Leak Input:")
    print("Original:", test_leak)
    print("Sanitized:", pii_detector.sanitize_input(test_leak))
