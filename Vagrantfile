# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.define "salt" do |salt|
    salt.vm.synced_folder "salt/", "/srv/salt/"

    # This is not good at all...
    $minion_config = <<EOF
sudo mkdir -p /etc/salt/minion.d
echo "grains:" | sudo tee /etc/salt/minion.d/development.conf
echo "  environment: development" | sudo tee -a /etc/salt/minion.d/development.conf
echo "  roles:" | sudo tee -a /etc/salt/minion.d/development.conf
echo "    - elasticsearch" | sudo tee -a /etc/salt/minion.d/development.conf
echo "    - logstash" | sudo tee -a /etc/salt/minion.d/development.conf
echo "    - kibana" | sudo tee -a /etc/salt/minion.d/development.conf
EOF

    salt.vm.provision "shell", inline: $minion_config

    salt.vm.provision :salt do |s|
      s.install_type = "daily"
      s.minion_config = "salt/masterless-minion"
      s.run_highstate = true
    end
  end

  # config.vm.define "ansible" do |ansible|
  #
  # end
end
