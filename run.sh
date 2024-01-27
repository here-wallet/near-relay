#!/bin/bash

# Default command with required arguments
CMD_ARGS=("uvicorn" "src.app:app" "--host" "0.0.0.0" "--port" "8000")

# Check for --ssl argument and append SSL configurations
for arg in "$@"; do
    if [[ $arg == "--ssl" ]]; then
        # Assume SSL key and cert are in /ssl/certs/
        # Modify this path as necessary
        CMD_ARGS+=("--ssl-keyfile=/ssl/certs/key.pem" "--ssl-certfile=/ssl/certs/cert.pem")
        break
    fi
done

# Execute the command with additional arguments from command line
exec "${CMD_ARGS[@]}" "$@"
