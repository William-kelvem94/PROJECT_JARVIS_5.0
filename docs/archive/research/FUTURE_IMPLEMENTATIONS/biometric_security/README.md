# Biometric Encryption Legacy Module

## Overview
This directory contains the legacy implementation of the biometric encryption system for PROJECT JARVIS 5.0. 

## Components
- **blackbox_legacy.py**: Implements `BlackBox` using SQLCipher for AES-256 encryption of biometric hashes.
- **sentinel_legacy.py**: Implements `SentinelSecurity`, handling HWID-based key derivation (Argon2id) to unlock the BlackBox.

## Deactivation Reason
The biometric encryption layer has been deactivated to increase system agility and remove the hardware-locked encryption requirement, while preserving the Facial Recognition (Level A/B/C) capabilities.

## Re-integration Guide
To re-enable biometric encryption:
1. Restore `blackbox_legacy.py` and `sentinel_legacy.py` to `backend/app/security/`.
2. Ensure `pysqlcipher3` and `argon2-cffi` are installed in the environment.
3. Update the system boot sequence to call `SentinelSecurity.authenticate_user_biometric()` before initializing the main brain.
