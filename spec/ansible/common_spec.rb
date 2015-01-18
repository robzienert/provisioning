require 'spec_helper'

describe package('ntp') do
  it { should be_installed }
end

describe service('ntp') do
  it { should be_enabled }
  it { should be_running }
end

describe package('unzip') do
  it { should be_installed }
end

describe package('python-pip') do
  it { should be_installed }
end

describe package('python-setuptools') do
  it { should be_installed }
end

describe package('htop') do
  it { should be_installed }
end

describe package('sysstat') do
  it { should be_installed }
end

describe package('dstat') do
  it { should be_installed }
end

describe package('git') do
  it { should be_installed }
end

describe package('bash') do
  it { should be_installed }
end

describe package('awscli') do
  it { should be_installed.by('pip') }
end

describe package('boto') do
  it { should be_installed.by('pip') }
end
