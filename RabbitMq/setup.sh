#  setup script for this project
#  will create a virtual env based on the given requirements.pip file

has_virtenv=`which virtualenv 2>&1 > /dev/null`
if [[ $has_virtenv -ne 0 ]]; then
  apt-get install python-virtualenv
fi

#  virtualenv now installed, create the env
virtualenv DEV

pip install -E DEV -r requirements.txt
