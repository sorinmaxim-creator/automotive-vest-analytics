#!/bin/bash
set -e

SSH_DIR="$HOME/.ssh"
KEY_NAME="vestpolicylab_key"
HOST="85.204.138.44"
USER="sorin"
ALIAS="serveradrvesta1"

echo "=== SSH Setup for $ALIAS ==="

# 1. Ensure .ssh directory exists
if [ ! -d "$SSH_DIR" ]; then
    echo "Creating directory: $SSH_DIR"
    mkdir -m 700 "$SSH_DIR"
fi

# 2. Copy Key if not exists
if [ ! -f "$SSH_DIR/$KEY_NAME" ]; then
    echo "Copying key to $SSH_DIR..."
    cp "ssh_setup/$KEY_NAME" "$SSH_DIR/$KEY_NAME"
    cp "ssh_setup/$KEY_NAME.pub" "$SSH_DIR/$KEY_NAME.pub"
    chmod 600 "$SSH_DIR/$KEY_NAME"
    chmod 644 "$SSH_DIR/$KEY_NAME.pub"
else
    echo "Key $KEY_NAME already exists in $SSH_DIR. Skipping copy."
fi

# 3. Update Config
CONFIG_BLOCK="
Host $ALIAS
    HostName $HOST
    User $USER
    IdentityFile ~/.ssh/$KEY_NAME
    IdentitiesOnly yes
"

if [ ! -f "$SSH_DIR/config" ]; then
    touch "$SSH_DIR/config"
    chmod 600 "$SSH_DIR/config"
fi

if grep -q "Host $ALIAS" "$SSH_DIR/config"; then
    echo "Host $ALIAS already configured in $SSH_DIR/config."
else
    echo "Adding configuration for $ALIAS to $SSH_DIR/config..."
    echo "$CONFIG_BLOCK" >> "$SSH_DIR/config"
fi

# 4. Copy ID to Server (Manual Step)
echo ""
echo "=== Manual Step Required ==="
echo "I have configured the keys and your SSH config file."
echo "To finish, you must copy the key to the server. I cannot do this for you because it requires your password."
echo ""
echo "Please run the following command in your terminal and enter your password when prompted:"
echo ""
echo "ssh-copy-id -i $SSH_DIR/$KEY_NAME.pub $USER@$HOST"
echo ""
echo "=== Setup of Local Configuration Complete ==="
