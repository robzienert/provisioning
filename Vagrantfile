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

    minion.vm.provision :salt do |salt|
      salt.install_type = "daily"
      salt.minion_config = "salt/minion"
      salt.run_highstate = true
      salt.minion_key = "salt/key/minion.pem"
      salt.grain_config = "salt/minion_grains"
    end
  end

  config.vm.define "ansible" do |ansible|
    ansible.vm.provider "virtualbox" do |v|
      v.memory = 2048
      v.cpus = 2
    end

    ansible.vm.hostname = "vagrant"
    ansible.vm.network :private_network, ip: "192.168.111.222"
    ansible.vm.provision :ansible do |a|
      a.playbook = "ansible/playbook.yml"
      a.inventory_path = "ansible/inventories/development"
      a.verbose = "v"
      a.limit = "vagrant"
    end

    # ansible.vm.provision :serverspec do |spec|
    #   spec.pattern = 'tests/*_spec.rb'
    # end
  end
end
