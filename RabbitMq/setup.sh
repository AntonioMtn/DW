#  setup script for this project
#  will create a virtual env based on the given requirements.pip file

current_dir=`pwd`

has_virtenv=`which virtualenv 2>&1 > /dev/null`
if [[ $has_virtenv -ne 0 ]]; then
  apt-get install python-virtualenv
fi

#  virtualenv now installed, create the env
virtualenv DEV

pip install -E DEV -r requirements.txt

#  flowd bindings are not available in pip
#   download flowd, build the C then install
#   with the virutalenv python
sudo apt-get install python-dev
mkdir tmp
wget https://flowd.googlecode.com/files/flowd-0.9.1.tar.gz -O tmp/flowd-0.9.1.tar.gz
cd tmp
tar -zxf flowd-0.9.1.tar.gz
cd flowd-0.9.1
./configure
make
sudo make install

$current_dir/DEV/bin/python setup.py install

