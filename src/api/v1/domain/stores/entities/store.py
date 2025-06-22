from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class Store:
    """
    Store Entity - Core business object for the Stores domain
    """

    id: Optional[int] = None
    nom: str = ""
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None

    def __post_init__(self):
        if not self.nom:
            raise ValueError("Store name is required")
        if self.email and not self._is_valid_email(self.email):
            raise ValueError("Invalid email format")

    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation"""
        if not email or not email.strip():
            return False
        # Basic email pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email.strip()))

    def update_contact_info(
        self, telephone: Optional[str] = None, email: Optional[str] = None
    ):
        """Update store contact information with validation"""
        if email and not self._is_valid_email(email):
            raise ValueError("Invalid email format")
        if telephone:
            self.telephone = telephone
        if email:
            self.email = email

    def is_contact_complete(self) -> bool:
        """Check if store has complete contact information"""
        return bool(self.telephone and self.email and self.adresse)
