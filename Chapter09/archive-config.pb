---
- name: Archive configuration
  hosts: junos
  gather_facts: no
  tasks:
  - junos_facts:
      gather_subset: config
    register: facts
  - copy: content="{{ facts.ansible_facts.ansible_net_config }}" dest="/var/tmp/{{ ansible_net_hostname }}.cfg"
