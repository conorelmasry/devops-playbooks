# devops-playbooks/terraform
A guide/reminder for setting up Terraform to provision VMs on a Proxmox host.
Included details to help setting up ansible.

## Preparing a template VM (On the host):
1. Download a "cloud-init" suitable image.
    - Wget an image from one of the following sources.
        - [Ubuntu Images](https://cloud-images.ubuntu.com/)
        - [Debian Images](https://cdimage.debian.org/images/cloud/)
    - If required, convert the image to .img using "qemu-img"
        ```
        qemu-img convert -f qcow2 -O raw /path/to/image.qcow2 /path/to/image.img
        ```

2. Update the image using "virt-customize".
    - Install the prerequisites on the host (first time only)
        ```
        apt update -y
        apt install libguestfs-tools -y
        ```
    - Install applications to the image
        ```
        virt-customize -a {image-name} --install {application-name}
        ```
    - **Required for Debian** - Apply networking fix
        ```
        virt-customize -a {image-name} \
        --run-command "printf 'Package: *\nPin: release n=trixie\nPin-Priority: 50' >> /etc/apt/preferences" \
        --run-command "printf '\nTypes: deb deb-src\nURIs: mirror+file:///etc/apt/mirrors/debian.list\nSuites: trixie\nComponents: main' >> /etc/apt/sources.list.d/debian.sources" \
        --run-command "apt-get update" \
        --run-command "apt-get install cloud-init/testing -y"
        ```

3. Prepare the template
    - Create the VM (which will later be converted)
        ```
        qm create {template-number} --name "{template-name}" --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0
        ```
    - Import the disk
        ```
        qm importdisk {template-number} {image-name} local-lvm
        ```
    - Prepare the interface
        ```
        qm set {template-number} --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-{template-number}-disk-0
        ```
    - Set the boot disk
        ```
        qm set {template-number} --boot c --bootdisk scsi0
        ```
    - Add the cloud-init disk
        ```
        qm set {template-number} --ide2 local-lvm:cloudinit
        ```
    - Add a serial display output
        ```
        qm set {template-number} --serial0 socket --vga serial0
        ```
    - *Optional* - Enable the agent
        ```
        qm set {template-number} --agent enabled=1
        ```
    - Convert the VM to a template
        ```
        qm template {template-number}
        ```
    
## Deploying an instance
To use this template, the following files are required:
- `vars.tf` using the variables from [vars.tf.sample](vars.tf.sample)

For ansible to work, the following additional files are required:
- `ansible.cfg` using the template [ansible.cfg.sample](../ansible.cfg.sample)
- A single hosts file, in one of the following formats:
    - `hosts.ini` using the template [hosts.ini.sample](../hosts.ini.sample)
    -  `hosts.yml` using the template [hosts.yml.sample](../hosts.yml.sample)
- A public/private keypair:
    - The private key must be referenced in `ansible.cfg`
    - The contents of the public key must be added to `vars.tf`

Optional additional files:
- A config file, to simplify ssh access:
    - See [config.sample](../config.sample)

## Ready to Deploy?
The VM can now be deployed using the following steps.
1. `terraform plan` - This will confirm the changes that are about to be made by terraform.
2. `terraform apply` - This will apply the changes.