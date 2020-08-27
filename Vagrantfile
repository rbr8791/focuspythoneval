# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
$setup_project = <<-"SCRIPT"
  cd /vagrant
  conda create -n default37 python=3 -y
  source activate default37
  clear
  pip install -r requirements.txt
  chmod ugo+x start-app.sh
  chmod ugo+x create-migration.sh
SCRIPT
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "continuumio/anaconda3"
  config.vm.hostname = "focuspythontest"

  # Plugin specific options
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder "./", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    vb.name = "itunescentos7"
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false

    # Customize the options
    vb.customize ["modifyvm", :id, "--memory", "2500", "--cpus", "3", "--ioapic", "on"]
  end

  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # config.vm.provision :shell, path: "start-app.sh", run: "always"

  config.vm.provision "shell", run: "always", privileged: false, inline: <<-SHELL
    server_ip=`ifconfig eth0 | grep broadcast | awk '{print $2}'`
    if ! [ -d "/home/vagrant/anaconda" ]; then
        sudo yum groupinstall -y "Development Tools" --nogpgcheck
        sudo yum install -y PyQt4 --exclude=kernel* --nogpgcheck
        sudo yum install -y wget --exclude=kernel* --nogpgcheck
        sudo yum install -y net-tools --nogpgcheck
        ANACONDA_INST=Anaconda3-4.1.1-Linux-x86_64.sh
        cd /home/vagrant
        if [ ! -s $ANACONDA_INST ] ; then
            echo "Trying to download $ANACONDA_INST"
            wget http://repo.continuum.io/archive/$ANACONDA_INST ./$ANACONDA_INST
        fi
        if [ -s $ANACONDA_INST ] ; then
          chmod +x $ANACONDA_INST
          ./$ANACONDA_INST -b -p /home/vagrant/anaconda
          echo PATH=/home/vagrant/anaconda/bin:$PATH >> /home/vagrant/.bashrc
        else
          echo "No Anaconda installer found"
        fi
        cd /vagrant

        export server_ip
        source /home/vagrant/.bashrc
        conda create -n default37 python=3 -y
        source activate default37
        clear
        pip install -r requirements.txt
        chmod ugo+x start-app.sh
        chmod ugo+x create-migration.sh
        source activate default37
        export FLASK_APP=iap.py
        export FLASK_ENV=development
        export FLASK_DEBUG=1
        export FLASK_RUN_PORT=5000
        export FLASK_RUN_HOST=${server_ip}
        flask run
    else
        cd /vagrant
        export server_ip
        source /home/vagrant/.bashrc
        source activate default37
        clear
        export FLASK_APP=iap.py
        export FLASK_ENV=development
        export FLASK_DEBUG=1
        export FLASK_RUN_PORT=5000
        export FLASK_RUN_HOST=${server_ip}
        flask run
    fi
  SHELL

end