---
- name: Conditional configuration
  hosts: junos
  gather_facts: no
  tasks:
  - junos_facts:
      gather_subset: config
    register: facts
  - junos_config:
      lines: 
      - set firewall filter BORDER term 10 from protocol icmp
      - set firewall filter BORDER term 10 then reject
      comment: Firewall filter update
    when: facts.ansible_facts.ansible_net_version == "15.1F6-S5.6"
#    when: inventory_hostname == "junos-vm"
#    when: development == 1
