#  setup script for this project
#  will create a virtual env based on the given requirements.pip file

current_dir=`pwd`

#  virtualenv now installed, create the env
venv_name=".venv"
virtualenv $venv_name

pip install -E $venv_name -r requirements.txt

#  flowd bindings are not available in pip
#   download flowd, build the C then install
#   with the virutalenv python
mkdir tmp
wget https://flowd.googlecode.com/files/flowd-0.9.1.tar.gz -O tmp/flowd-0.9.1.tar.gz
cd tmp
tar -zxf flowd-0.9.1.tar.gz
cd flowd-0.9.1
./configure
make

$current_dir/$venv_name/bin/python setup.py install

#  create the activation script
echo ". ${current_dir}/$venv_name/bin/activate" > ${current_dir}/activate
