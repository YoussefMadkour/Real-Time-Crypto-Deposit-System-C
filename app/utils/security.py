import re
from typing import Optional


def is_valid_ethereum_address(address: str) -> bool:
    """
    Validate Ethereum address format.
    
    Args:
        address: The address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not address:
        return False
    
    # Check if it starts with 0x and is 42 characters long
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    
    return True


def normalize_address(address: str) -> str:
    """
    Normalize Ethereum address to lowercase.
    
    Args:
        address: The address to normalize
        
    Returns:
        str: Normalized address
    """
    if not address:
        return address
    
    return address.lower()


def validate_transaction_hash(tx_hash: str) -> bool:
    """
    Validate Ethereum transaction hash format.
    
    Args:
        tx_hash: The transaction hash to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not tx_hash:
        return False
    
    # Check if it starts with 0x and is 66 characters long
    if not re.match(r'^0x[a-fA-F0-9]{64}$', tx_hash):
        return False
    
    return True


def normalize_transaction_hash(tx_hash: str) -> str:
    """
    Normalize transaction hash to lowercase.
    
    Args:
        tx_hash: The transaction hash to normalize
        
    Returns:
        str: Normalized transaction hash
    """
    if not tx_hash:
        return tx_hash
    
    return tx_hash.lower()
