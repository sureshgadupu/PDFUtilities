import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class PasswordManager:
    """Manages frequently used PDF passwords with associated names"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.pdf_utilities'
        self.passwords_file = self.config_dir / 'saved_passwords.json'
        self._ensure_config_dir()
        self.passwords = self._load_passwords()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_passwords(self) -> Dict[str, str]:
        """Load saved passwords from file
        
        Returns:
            Dict mapping password names to password values
        """
        if not self.passwords_file.exists():
            return {}
        
        try:
            with open(self.passwords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('passwords', {})
        except Exception as e:
            print(f"Error loading passwords: {e}")
            return {}
    
    def _save_passwords(self):
        """Save passwords to file"""
        try:
            with open(self.passwords_file, 'w', encoding='utf-8') as f:
                json.dump({'passwords': self.passwords}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving passwords: {e}")
    
    def add_password(self, name: str, password: str) -> bool:
        """Add a new password with a name
        
        Args:
            name: Display name for the password
            password: The actual password
            
        Returns:
            True if added successfully, False if name already exists
        """
        if not name or not password:
            return False
        
        if name in self.passwords:
            return False
        
        self.passwords[name] = password
        self._save_passwords()
        return True
    
    def update_password(self, old_name: str, new_name: str, password: str) -> bool:
        """Update an existing password
        
        Args:
            old_name: Current name of the password
            new_name: New name for the password
            password: The password value
            
        Returns:
            True if updated successfully
        """
        if old_name in self.passwords:
            # Remove old entry
            del self.passwords[old_name]
        
        # Add with new name
        self.passwords[new_name] = password
        self._save_passwords()
        return True
    
    def remove_password(self, name: str) -> bool:
        """Remove a password by name
        
        Args:
            name: Name of the password to remove
            
        Returns:
            True if removed successfully
        """
        if name in self.passwords:
            del self.passwords[name]
            self._save_passwords()
            return True
        return False
    
    def get_password(self, name: str) -> Optional[str]:
        """Get a password by name
        
        Args:
            name: Name of the password
            
        Returns:
            The password or None if not found
        """
        return self.passwords.get(name)
    
    def get_all_passwords(self) -> Dict[str, str]:
        """Get all saved passwords
        
        Returns:
            Dictionary mapping names to passwords
        """
        return self.passwords.copy()
    
    def get_password_names(self) -> List[str]:
        """Get list of all password names
        
        Returns:
            List of password names
        """
        return sorted(self.passwords.keys())
    
    def clear_all(self):
        """Clear all saved passwords"""
        self.passwords.clear()
        self._save_passwords()

