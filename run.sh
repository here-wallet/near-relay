#!/bin/bash

# Default command
set -- uvicorn src.app:app --host 0.0.0.0 --port 8000 "$@"

# Check for --ssl argument
if [[ " $* " == *" --ssl "* ]]; then
    # Assume SSL key and cert are in /path/to/your/certs/
    # Modify this path as necessary
    set -- "$@" --ssl-keyfile=/ssl/certs/key.pem --ssl-certfile=/ssl/certs/cert.pem
fi

# Execute the command
exec "$@"
