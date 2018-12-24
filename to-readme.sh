
rm -rf parse_files/;
rm main.py
rm README.md

jupyter nbconvert --to python parse.ipynb
jupyter nbconvert --to markdown parse.ipynb

mv parse.py main.py
mv parse.md README.md

