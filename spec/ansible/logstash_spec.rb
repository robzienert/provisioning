require 'spec_helper'

describe service('logstash') do
  it { should be_enabled }
  it { should be_running }
end
