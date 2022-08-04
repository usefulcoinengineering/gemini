Run the following commands to rapid setup:

```bash
git clone https://github.com/usefulcoinengineering/gemini.git
cd gemini
cp examples/example-credentials.py libraries/credentials.py
sudo apt install python3-pip
pip3 install websocket-client
pip3 install boto3
sudo timedatectl set-timezone America/Jamaica
```

Notes:

1. You need to edit credentials.py and add your real Gemini API credentials.
2. You may need to execute the following command to install pip3 before installing the websocket-client library:

```bash
sudo apt install python3-pip
```

Logfiles:

To make it easier to read the logfiles:

```bash
sudo timedatectl set-timezone America/Jamaica
```

Amazon Support:

1. To get SNS support, open up IAM and add a new user that has privileges to send messages.
2. Copy the credentials to the EC2 instance (or MacBook Pro) used for trading:

```bash
mkdir ~/.aws
cat > ~/.aws/config << EOF
[default]
region=us-east-1
EOF
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = AKIARB33NP5HGWSP145K
aws_secret_access_key = c/MVoL9wOiKnt4fyPhKRWOt@hqqKhfvLcon!oZJ/
```
