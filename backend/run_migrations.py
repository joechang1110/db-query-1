#!/usr/bin/env python
"""Run Alembic migrations."""

import sys
import os
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Add current directory to path
sys.path.insert(0, str(script_dir))

try:
    # Try importing alembic modules
    try:
        from alembic import command
        from alembic.config import Config
    except ImportError:
        # Fallback: use alembic.config.main
        from alembic.config import main as alembic_main
        import sys as sys_module
        
        print("Running database migrations...")
        # Call alembic main with upgrade head arguments
        sys_module.argv = ['alembic', 'upgrade', 'head']
        alembic_main()
        print("Migrations completed successfully!")
        sys.exit(0)
    
    # Get the directory where this script is located
    alembic_ini = script_dir / "alembic.ini"
    
    # Create config
    cfg = Config(str(alembic_ini))
    
    # Run upgrade
    print("Running database migrations...")
    command.upgrade(cfg, "head")
    print("Migrations completed successfully!")
    sys.exit(0)
except Exception as e:
    print(f"Error running migrations: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

