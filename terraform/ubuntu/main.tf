resource "proxmox_vm_qemu" "cloudinit-example" {
  vmid        = 1000
  name        = "test-terraform0"
  target_node = "macmini"
  agent       = 1
  cores       = 2
  memory      = 2048
  boot        = "order=scsi0" # has to be the same as the OS disk of the template
  clone       = var.template_name # The name of the template
  scsihw      = "virtio-scsi-single"
  vm_state    = "running"
  automatic_reboot = true

  # Cloud-Init configuration
  #cicustom   = "vendor=local:snippets/qemu-guest-agent.yml" # /var/lib/vz/snippets/qemu-guest-agent.yml
  ciupgrade  = true
  nameserver = var.dns
  ipconfig0  = var.ipconfig
  skip_ipv6  = true
  #ciuser     = "root" # leave as default
  #cipassword = "Enter123!"
  sshkeys    = var.ssh_key
  # Most cloud-init images require a serial device for their display
  serial {
    id = 0
  }

  disks {
    scsi {
      scsi0 {
        # We have to specify the disk from our template, else Terraform will think it's not supposed to be there
        disk {
          storage = "local-lvm"
          # The size of the disk should be at least as big as the disk in the template. If it's smaller, the disk will be recreated
          size    = "20G" 
        }
      }
    }
    ide {
      # Some images require a cloud-init disk on the IDE controller, others on the SCSI or SATA controller
      ide1 {
        cloudinit {
          storage = "local-lvm"
        }
      }
    }
  }

  network {
    bridge = "vmbr0"
    model  = "virtio"
  }
}

terraform {
  required_providers {
    proxmox = {
      source = "Telmate/proxmox"
      version = "3.0.1-rc4"
    }
  }
}
provider "proxmox" {
  pm_api_url = "https://macmini.home:8006/api2/json"

  pm_api_token_id = var.pm_api_token_id

  pm_api_token_secret = var.pm_api_token_secret
}