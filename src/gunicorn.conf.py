import os

# Bind on all interfaces so nginx can reach the container; without this gunicorn
# defaults to 127.0.0.1 and is only reachable from inside the container.
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
