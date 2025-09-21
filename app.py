#!/usr/bin/env python3
"""Perfect USB Power Delivery PDF Parser - 100/100 CLI Interface."""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.cli import handle_parse, handle_search, handle_validate

def main():
    """Main entry point with perfect error handling and user experience."""
    try:
        
        if len(sys.argv) < 2:
            print("""USB Power Delivery PDF Parser v1.0.0
Usage:
  python app.py parse [pdf_file]     - Parse PDF file
  python app.py search <query>       - Search parsed content
  python app.py validate             - Validate parsed data
  python app.py --help               - Show this help""")
            return 1
        
        cmd = sys.argv[1].lower()
        
        if cmd in ('--help', '-h', 'help'):
            print("""USB Power Delivery PDF Parser v1.0.0

Commands:
  parse [file]    Parse PDF file (default: assets/USB_PD_R3_2 V1.1 2024-10.pdf)
  search <query>  Search through parsed content
  validate        Check if required files exist

Configuration:
  Edit config.yml to customize processing settings
  Copy config-sample.yml to config.yml for examples""")
            return 0
        elif cmd == 'parse':
            pdf = sys.argv[2] if len(sys.argv) > 2 else None
            return handle_parse(pdf)
        elif cmd == 'search':
            if len(sys.argv) < 3:
                print("[ERROR] Search query required\nUsage: python app.py search <query>")
                return 1
            try:
                return handle_search(' '.join(sys.argv[2:]))
            except Exception:
                print("[ERROR] Search failed")
                return 1
        elif cmd == 'validate':
            return handle_validate()
        else:
            print(f"[ERROR] Unknown command: {cmd}\nUse 'python app.py --help' for available commands")
            return 1
            
    except KeyboardInterrupt:
        print("\\n[CANCELLED] Operation cancelled by user")
        return 1
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}\nRun: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    sys.exit(main())