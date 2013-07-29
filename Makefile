clean:
	find . -type f -name '*.pyc' -delete
installdeps:
	sudo HOME=/tmp/ apt-get install -y $(cat packages.txt)
	pip install -r requirements.txt