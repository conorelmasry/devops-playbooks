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
        sudo apt update -y
        sudo apt install libguestfs-tools -y
        ```
    - Install applications to the image
        ```
        sudo virt-customize -a {image-name} --install {application-name}
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
        sudo qm create 9000 --name "{template-name}" --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0
        ```
    - Import the disk
        ```
        sudo qm importdisk 9000 {image-name} local-lvm
        ```
    - Prepare the interface
        ```
        sudo qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-zfs:vm-9000-disk-0
        ```
    - Set the boot disk
        ```
        sudo qm set 9000 --boot c --bootdisk scsi0
        ```
    - Add the cloud-init disk
        ```
        sudo qm set 9000 --ide2 local-zfs:cloudinit
        ```
    - Add a serial display output
        ```
        sudo qm set 9000 --serial0 socket --vga serial0
        ```
    - *Optional* - Enable the agent
        ```
        sudo qm set 9000 --agent enabled=1
        ```
    - Convert the VM to a template
        ```
        sudo qm template 9000
        ```
    