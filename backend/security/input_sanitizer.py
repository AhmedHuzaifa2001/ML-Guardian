import sys
from pathlib import Path

# Add backend directory to path so we can run this file directly
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import re
import logfire
from config import settings


class SanitizationException(Exception):
    """Custom exception for input validation failures."""
    pass


class InputSanitizer:
    def __init__(self):
        self.max_length = settings.MAX_INPUT_LENGTH  # From .env (5000 chars)
        
        # Patterns that indicate encoding attacks or suspicious content
        self.suspicious_patterns = [
            r'<script.*?>',           # XSS script tags
            r'javascript:',           # JavaScript URI injection
            r'data:text/html',        # Data URI injection
            r'\\x[0-9a-fA-F]{2}',    # Hex-encoded characters
            r'\\u[0-9a-fA-F]{4}',    # Unicode escape sequences
            r'\{\{.*?\}\}',           # Template injection (e.g., Jinja2)
            r'\$\{.*?\}',            # Expression injection
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.suspicious_patterns]

    def sanitize(self, user_input: str) -> str:
        """
        Validates and sanitizes user input.
        Raises SanitizationException if input fails validation.
        Returns the cleaned input string.
        """
        with logfire.span("Security Layer: Input Sanitization"):
            # 1. Check for empty input
            if not user_input or not user_input.strip():
                raise SanitizationException("Input cannot be empty.")
            
            # 2. Strip leading/trailing whitespace
            cleaned = user_input.strip()
            
            # 3. Check max length
            if len(cleaned) > self.max_length:
                logfire.warn(f"Input exceeded max length: {len(cleaned)} > {self.max_length}")
                raise SanitizationException(f"Input exceeds maximum allowed length of {self.max_length} characters.")
            
            # 4. Check for suspicious encoding patterns
            for pattern in self.compiled_patterns:
                if pattern.search(cleaned):
                    logfire.warn(f"Suspicious pattern detected: {pattern.pattern}")
                    raise SanitizationException("Input contains suspicious encoding or injection patterns.")
            
            # 5. Remove null bytes (common attack vector)
            cleaned = cleaned.replace('\x00', '')
            
            logfire.info("Input passed sanitization checks.")
            return cleaned


# Create a single instance
input_sanitizer = InputSanitizer()


if __name__ == "__main__":
    logfire.configure()
    
    # Test cases
    tests = [
        ("Normal ML question", "What is the best model for image classification?"),
        ("Too long input", "A" * 6000),
        ("XSS attack", "Hello <script>alert('hacked')</script>"),
        ("Template injection", "Tell me about {{config.SECRET_KEY}}"),
        ("Empty input", "   "),
    ]
    
    for name, test_input in tests:
        print(f"Testing: {name}")
        try:
            result = input_sanitizer.sanitize(test_input)
            print(f"  -> Passed! Output: '{result[:50]}...'\n")
        except SanitizationException as e:
            print(f"  -> Blocked: {e}\n")
