"""Web tool wrappers for executing whatweb, wafw00f, and nikto via subprocess."""

import subprocess
import shutil
from typing import List, Optional
from axiom.config.settings import settings


class WebToolScanner:
    """Base class for web scanning tools."""

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout or settings.general_tool_timeout

    def _verify_binary(self, binary: str) -> None:
        """Verify binary is available on the system."""
        if not shutil.which(binary):
            raise RuntimeError(
                f"{binary} not found. Please install it on your system."
            )

    def _run_cmd(self, cmd: List[str]) -> str:
        """Execute command safely and return output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return f"[TIMEOUT] Execution exceeded {self.timeout}s"
        except Exception as e:
            return f"[ERROR] {str(e)}"


class WhatWebScanner(WebToolScanner):
    """Wrapper for WhatWeb technology identifier."""

    def __init__(self, timeout: Optional[int] = None):
        super().__init__(timeout)
        self._verify_binary("whatweb")

    def scan(self, target: str) -> str:
        """Identify technologies on the target URL."""
        # Ensure it's a URL-like string for whatweb
        if not target.startswith(("http://", "https://")):
            target = f"http://{target}"
        
        cmd = ["whatweb", "--color=never", "--no-errors", target]
        return self._run_cmd(cmd)


class Wafw00fScanner(WebToolScanner):
    """Wrapper for Wafw00f WAF detector."""

    def __init__(self, timeout: Optional[int] = None):
        super().__init__(timeout)
        self._verify_binary("wafw00f")

    def scan(self, target: str) -> str:
        """Detect WAF on the target URL."""
        if not target.startswith(("http://", "https://")):
            target = f"http://{target}"
            
        cmd = ["wafw00f", target]
        return self._run_cmd(cmd)


class NiktoScanner(WebToolScanner):
    """Wrapper for Nikto web vulnerability scanner."""

    def __init__(self, timeout: Optional[int] = None):
        # Nikto can be slow, use a longer default timeout if not provided
        timeout = timeout or (settings.general_tool_timeout * 5)
        super().__init__(timeout)
        self._verify_binary("nikto")

    def scan(self, target: str) -> str:
        """Scan target URL for vulnerabilities."""
        if not target.startswith(("http://", "https://")):
            target = f"http://{target}"
            
        cmd = ["nikto", "-h", target, "-Tuning", "123b", "-maxtime", str(self.timeout)]
        return self._run_cmd(cmd)
