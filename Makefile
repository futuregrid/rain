VERSION = `python -c "import futuregrid; print futuregrid.RELEASE"`

all:
	make clean
	cd /tmp
	rm -rf /tmp/vc
	mkdir -p /tmp/vc
	cd /tmp/vc; git clone git://github.com/futuregrid/rain.git
	cd /tmp/vc/rain/doc; ls; make website
	cp -r /tmp/vc/rain/doc/build/web-${VERSION}/* .
	find . -name "*.pyc" -exec rm {} \;
	git add .
	git reset -- src
	git reset -- .nojekyll .project.bk .pydevproject .settings
	git commit -a -m "updating the github pages"
#	git commit -a _sources
#	git commit -a _static
	git push
	git checkout master
	rm -rf /tmp/vc
all-devmode:
	make clean
	cd /tmp
	rm -rf /tmp/vc
	mkdir -p /tmp/vc
	cd /tmp/vc; git clone git://github.com/futuregrid/rain.git
	git checkout master
	cd /tmp/vc/rain/doc; ls; make website
	git checkout gh-pages
	cp -r /tmp/vc/rain/doc/build/web-${VERSION}/* .
	find . -name "*.pyc" -exec rm {} \;
	rm -f .project
	git add .
	git reset -- src
	git reset -- .nojekyll .project.bk .pydevproject .settings
	git commit -a -m "updating the github pages"
	git push
	git checkout master
	rm -rf /tmp/vc
clean:
	find . -name "*~" -exec rm {} \;  
	find . -name "*.pyc" -exec rm {} \;  
	rm -rf build dist *.egg-info *~ #*
	rm -f distribute*.gz distribute*.egg 
