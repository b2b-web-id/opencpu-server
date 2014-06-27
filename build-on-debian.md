# Build OpenCPU cloud server on Debian
# Tested only with Debian 7.0 Wheezy

# Notes: Most depe

All instructions below must be executed with `sudo` or as `root` user.

## Install and enable AppArmor

	#become root
	sudo -i 

	#Install apparmor
	sudo apt-get install apparmor-utils

	## Edit /etc/default/grub to set:
	GRUB_CMDLINE_LINUX=" security=apparmor"

	#Update and reboot
	update-grub
	reboot

	#Test that apparmor works
	aa-status

## Build and install rApache (mod_R)

	#Need R at least 3.0, see http://cran.us.r-project.org/bin/linux/debian/
	apt-key adv --keyserver subkeys.pgp.net --recv-key 381BA480
	echo "deb http://cran.r-project.org/bin/linux/debian wheezy-cran3/" > /etc/apt/sources.list.d/cran.list

	#update all
	apt-get update
	apt-get upgrade

	#install rapache(mod_R) build dependencies
	apt-get install git make devscripts apache2-prefork-dev apache2-mpm-prefork libapreq2-dev r-base-core r-base-dev

	#build rapache (libapache2-mod-r-base)
	git clone https://github.com/jeffreyhorner/rapache.git
	cd rapache
	debuild -us -uc

	#Install rapache
	cd ..
	dpkg -i libapache2*.deb
	service apache2 restart

## Build and install OpenCPU

	#install opencpu build dependencies
	apt-get install r-base libapparmor-dev r-cran-rcpp libcurl4-openssl-dev xvfb xauth xfonts-base

	#build opencpu
	git clone https://github.com/jeroenooms/opencpu-deb
	cd opencpu-deb
	debuild -us -uc

	#install opencpu
	cd ..
	dpkg -i opencpu-lib*.deb
	dpkg -i opencpu-server*.deb
	dpkg -i opencpu-cache*.deb