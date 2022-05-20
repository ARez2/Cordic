apt update -y
apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev git
wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz
tar -xf Python-3.9.1.tgz
cd Python-3.9.1

./configure --enable-optimizations
make -j4
make altinstall
python3.9 -m pip install -r requirements.txt
python3.9 -c "from src.lib.utils import _override_database as o;o()"
python3.9 cordic.py 