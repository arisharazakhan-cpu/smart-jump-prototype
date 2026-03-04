import os
from smartjump.ui import run_ui

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run_ui(host="0.0.0.0", port=port, open_browser=False)
