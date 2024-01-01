#!/usr/bin/env bash
set -e -x

# Set the working directory
WORKDIR=$(cd "$(dirname "$0")" && pwd)
export WORKDIR

# Create and activate a virtual environment
VENV=$(realpath "$PWD")/venv
if [[ ! -d $VENV ]]; then
    virtualenv -p python3 "$VENV" || python3 -m venv "$VENV"
fi

activate_venv() {
    # Activate the virtual environment
    source "$WORKDIR/venv/bin/activate"
}

# Install dependencies
echo "Installing dependencies"
activate_venv && pip3 install -r requirements.txt

# Run the setup script
activate_venv && python ec2_instances.py

# Source environment variables
source environment_vars.txt
echo "INSTANCE_IP_MASTER_IP=$INSTANCE_IP_MASTER_IP"
echo "INSTANCE_IP_CHILD_IP_0=$INSTANCE_IP_CHILD_IP_0"
echo "INSTANCE_IP_CHILD_IP_1=$INSTANCE_IP_CHILD_IP_1"
echo "INSTANCE_IP_CHILD_IP_2=$INSTANCE_IP_CHILD_IP_2"
echo "INSTANCE_IP_PROXY_IP=$INSTANCE_IP_PROXY_IP"
echo "PRIVATE_KEY_FILE=$PRIVATE_KEY_FILE"
chmod 600 "$PRIVATE_KEY_FILE"

wait_until_instance_running () {
    # Wait until the SSH service is running on the instance
    SSH_IS_NOT_RUNNING=1
    while [[ $SSH_IS_NOT_RUNNING -eq 1 ]]; do
        nc -vzw 1 "$1" 22
        SSH_IS_NOT_RUNNING=$?
        if [[ $SSH_IS_NOT_RUNNING -eq 1 ]]; then
            echo "ssh not started yet, trying again in 3s..."; 
            sleep 3s;
        else
            echo "ssh started for $1";
        fi
    done
}

echo "Installing mysql cluster management on $INSTANCE_IP_MASTER_IP..."
# Copy and run the install script on the master node
scp -o "StrictHostKeyChecking no" -i "$PRIVATE_KEY_FILE" master_node.sh ubuntu@"$INSTANCE_IP_MASTER_IP":~
ssh -o "StrictHostKeyChecking no" -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP_MASTER_IP" 'chmod +x master_node.sh && sudo ./master_node.sh'

# Install MySQL Cluster on child nodes
for INSTANCE_IP in "$INSTANCE_IP_CHILD_IP_0" "$INSTANCE_IP_CHILD_IP_1" "$INSTANCE_IP_CHILD_IP_2"; do
    wait_until_instance_running "$INSTANCE_IP"
    echo "Installing mysql cluster on $INSTANCE_IP : copying install script..."
    scp -o "StrictHostKeyChecking no" -i "$PRIVATE_KEY_FILE" slave_node.sh ubuntu@"$INSTANCE_IP":~
    echo "Running script..."
    ssh -o "StrictHostKeyChecking no" -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP" 'chmod +x slave_node.sh && sudo ./slave_node.sh'
    echo "mysql cluster installed"
done

# Copy MySQL configurations to child nodes
for INSTANCE_IP in "$INSTANCE_IP_CHILD_IP_0" "$INSTANCE_IP_CHILD_IP_1" "$INSTANCE_IP_CHILD_IP_2"; do
    scp -i "$PRIVATE_KEY_FILE" systemd/ndbd.service master_node/my.cnf ubuntu@"$INSTANCE_IP":~
    ssh -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP" 'sudo mkdir -p /opt/mysqlcluster/deploy/mysqld_data && \
                                        sudo cp ndbd.service /etc/systemd/system/ && \
                                        sudo systemctl daemon-reload'
done

# Install MySQL Server on the master node
echo "Installing mysql-server on the management node"
scp -i "$PRIVATE_KEY_FILE" master_node/config.ini mysql_server.sh master_node/server_conf.conf ubuntu@"$INSTANCE_IP_MASTER_IP":~
ssh -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP_MASTER_IP" 'chmod +x mysql_server.sh && sudo ./mysql_server.sh'

echo "Successfully started master node"

# Start MySQL Cluster on child nodes
for INSTANCE_IP in "$INSTANCE_IP_CHILD_IP_0" "$INSTANCE_IP_CHILD_IP_1" "$INSTANCE_IP_CHILD_IP_2"; do
    ssh -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP" 'sudo systemctl start ndbd.service && \
                                        sudo systemctl status ndbd.service'
done
echo "Successfully started child nodes"

# Restart MySQL on master node and show management information
ssh -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP_MASTER_IP" 'sudo systemctl restart mysql && \
                                        ndb_mgm -e show'

echo "Successfully set up the cluster!"

# Deploy Flask app on the proxy node
scp -o "StrictHostKeyChecking no" -i "$PRIVATE_KEY_FILE" app.py private_key_PROJET_KEY.pem ubuntu@"$INSTANCE_IP_PROXY_IP":~
ssh -o "StrictHostKeyChecking no" -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP_PROXY_IP" 'chmod 755 app.py && \
                                                           export FLASK_APP=/home/ubuntu/app.py && \
                                                           sudo flask run --host 0.0.0.0 --port 80'
