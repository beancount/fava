# -*- mode: ruby -*-
# vi: set ft=ruby :
#
# These VM images are mainly for building binaries with PyInstaller for
# various platforms.  The distributions should have an old glibc if possible,
# as ABI compatibility should enable them to run on any more current version.
# The frontend code needs to be bundled before building the binaries.
# Current images:
#
# - CentOS 7 - build for 64bit Linux
# - OS X El Capitan (10.11) - build for 64bit MacOS

unless Vagrant.has_plugin?("vagrant-scp")
  raise 'Please run `vagrant plugin install vagrant-scp` to use this Vagrantfile.'
end

centos_install = <<-SHELL
    yum install -y https://centos7.iuscommunity.org/ius-release.rpm epel-release
    yum update -y
    yum install -y gcc python35u python35u-devel python35u-setuptools python35u-pip
SHELL

darwin_install = <<-SHELL
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew update
    brew install python3
SHELL

centos_build = <<-SHELL
    yum update -y
    pip3.5 install -U https://github.com/pyinstaller/pyinstaller/archive/develop.zip
    pip3.5 install -U /vagrant/fava
    make -C /vagrant/fava pyinstaller
SHELL

darwin_build = <<-SHELL
    brew update && brew upgrade && brew cleanup
    pip3 install -U https://github.com/pyinstaller/pyinstaller/archive/develop.zip
    pip3 install -U /vagrant/fava
    make -C /vagrant/fava pyinstaller
SHELL

Vagrant.configure("2") do |config|
    config.vm.synced_folder ".", "/vagrant/fava", type: "rsync", rsync__chown: false
    config.vm.synced_folder ".", "/vagrant", disabled: true

    config.vm.define "centos" do |b|
        b.vm.box = "centos/7"
        b.vm.provision "Install dependencies", type: "shell", inline: centos_install
        b.vm.provision "Build binary", type: "shell", inline: centos_build, run: "always"
    end

    config.vm.define "darwin" do |b|
        b.vm.box = "jhcook/osx-elcapitan-10.11"
        b.vm.provision "Fix shared folder permissions", type: "shell", inline: "chown -R vagrant /vagrant"
        b.vm.provision "Install dependencies", type: "shell", privileged: false, inline: darwin_install
        b.vm.provision "Build binary", type: "shell", privileged: false, inline: darwin_build, run: "always"
    end
end
