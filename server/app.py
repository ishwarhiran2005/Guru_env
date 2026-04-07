"""
OpenEnv Server Application.

This module provides the server entry point for OpenEnv deployment.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.sos_env import SOSEnv


def main():
    """Main entry point for the OpenEnv server."""
    print("SOS Environment Server - OpenEnv Mode")
    print("Environment is ready for OpenEnv deployment")
    
    # For now, this is a placeholder
    # OpenEnv will handle the actual server setup
    pass


if __name__ == "__main__":
    main()
