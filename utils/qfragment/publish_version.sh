
# confirm user updated version number
echo 'did you updated the version number in setup.py? y/N'
read answer
if [ "$answer" != "y" ];
then
  exit 1
fi


# confirm necessary tensorflow models are included 
echo 'does your package have all the necessary tensorflow models in it? y/N'
read answer
if [ "$answer" != "y" ];
then
  exit 1
fi

# delete old egg
rm -r *.egg-info 

# create new dist
python setup.py bdist_wheel --universal

# upload dist to pypi
twine upload dist/*
