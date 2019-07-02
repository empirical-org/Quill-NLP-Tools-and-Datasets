echo 'Install Homebrew'
if which brew > /dev/null; then
  echo 'Already installed'
else
  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

echo 'Update Homebrew'
brew update

echo 'Install python basics'
brew install python3
brew install freetype
brew install llvm
brew install libomp

pip3 install virtualenv
export PATH=/usr/local/opt/python/libexec/bin:$PATH

echo 'start virtualenv'
virtualenv env --python python3
source env/bin/activate

echo 'Install requirements'
pip3 install tensorflow
pip3 install spacy
python3 -m spacy download en
pip3 install -r requirements.txt

echo 'close session'
deactivate
