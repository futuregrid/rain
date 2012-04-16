VERSION = `python -c "import futuregrid; print futuregrid.RELEASE"`

all:
	cd /tmp
	rm -rf /tmp/vc
	mkdir -p /tmp/vc
	cd /tmp/vc; git clone git://github.com/futuregrid/rain.git
	cd /tmp/vc/rain/doc; ls; make website
	cp -r /tmp/vc/rain/doc/build/web-${VERSION}/* .
	git add .
	git commit -a -m "updating the github pages"
#	git commit -a _sources
#	git commit -a _static
	git push
	git checkout master

clean:
	find . -name "*~" -exec rm {} \;  
	find . -name "*.pyc" -exec rm {} \;  
	rm -rf build dist *.egg-info *~ #*
	rm -f distribute*.gz distribute*.egg 
