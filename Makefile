all:
	python setup.py sdist
	mv dist/net.worldtext.sms* .
	make clean
	
clean:
	rm -rf build dist net.worldtext.sms.egg-info
