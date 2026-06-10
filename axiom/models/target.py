"""Data models for target input and validation."""

from pydantic import BaseModel, field_validator
from typing import Literal
import ipaddress
import re


class Target(BaseModel):
    """Represents a scan target (domain, IP, or CIDR)."""

    value: str
    target_type: Literal["domain", "ip", "cidr", "url"] = "domain"

    @field_validator("value")
    @classmethod
    def validate_target(cls, v: str) -> str:
        """Validate and normalize target input."""
        v = v.strip()
        if not v:
            raise ValueError("Target cannot be empty")

        # Check if it's a URL
        if v.startswith(("http://", "https://")):
            return v

        # Check if it's a CIDR
        try:
            ipaddress.ip_network(v, strict=False)
            return v
        except ValueError:
            pass

        # Check if it's an IP address
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass

        # Check if it's a valid domain or hostname
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        )
        hostname_pattern = re.compile(r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$')
        
        if domain_pattern.match(v) or hostname_pattern.match(v):
            return v

        raise ValueError(f"Invalid target format: {v}. Must be a domain, IP, CIDR, or URL.")

    def get_scan_target(self) -> str:
        """Extract the hostname/IP for scanning (removes protocol from URLs)."""
        if self.value.startswith(("http://", "https://")):
            from urllib.parse import urlparse
            parsed = urlparse(self.value)
            return parsed.hostname or self.value
        return self.value

    def is_network_target(self) -> bool:
        """Check if target is suitable for network scanning (IP or CIDR)."""
        try:
            ipaddress.ip_network(self.value, strict=False)
            return True
        except ValueError:
            try:
                ipaddress.ip_address(self.value)
                return True
            except ValueError:
                return False