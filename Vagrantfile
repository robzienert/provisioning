# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.define "salt-master" do |master|
    master.vm.synced_folder "salt/", "/srv/salt/"

    master.vm.host_name = "master"
    master.vm.network :private_network, ip: "192.168.75.1"
    master.vm.network "public_network", :bridge => 'en0: Wi-Fi (AirPort)'

    master.vm.provision :salt do |salt|
      salt.install_master = true
      salt.no_minion = true
      salt.install_type = "daily"
      salt.always_install = true
      salt.master_config = "salt/master"
      # salt.seed_master = {
      #     "minion" => "/srv/salt/key/minion.pub"
      # }
    end
  end

  config.vm.define "salt" do |minion|
    minion.vm.synced_folder "salt/", "/srv/salt/"

    minion.vm.provision "shell", inline: "echo 'minion' | sudo tee /"
    minion.vm.provision :salt do |salt|
      salt.install_type = "daily"
      salt.minion_config = "salt/minion"
      salt.run_highstate = true
      salt.minion_key = "salt/key/minion.pem"
      salt.grain_config = "salt/minion_grains"
    end
  end

  # config.vm.define "ansible" do |ansible|
  #
  # end
end
