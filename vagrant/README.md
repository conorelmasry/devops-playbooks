# devops-playbooks/vagrant
A guide/reminder for provisioning custom Vagrant boxes, and deploying them using Vagrantfiles

## Preparing the box
1. Chose a starting point
    - Decide on an initial image to use for your VM.
        - [netboot.xyz](netboot.xyz)
        - [Ubuntu Images](https://cloud-images.ubuntu.com/)
        - [Debian Images](https://cdimage.debian.org/images/cloud/)
    - Create a VM in Virtualbox, with the following details:
        - Set the name to the final name of the box
        - Set the hard disk type to `vmdk`
        - Disable audio
        - Enable port forwarding of `guest:22` to `host:2222`
2. Configure the VM
    - Launch the VM and install the OS
        - Set the default user to `vagrant`
        - Set both user and root passwords to `vagrant`
    - Once installed, ensure the default user is superuser
        - Ensure `sudo` is installed
        - Edit `/etc/sudoers.d/vagrant` and add the following line: `vagrant ALL=(ALL) NOPASSWD:ALL`
    - Install the "Vagrant insecure key" (this will be replaced each time the box is brought up)
        ```
        mkdir -p /home/vagrant/.ssh
        chmod 0700 /home/vagrant/.ssh
        wget --no-check-certificate \
        https://raw.github.com/hashicorp/vagrant/master/keys/vagrant.pub \
        -O /home/vagrant/.ssh/authorized_keys
        chmod 0600 /home/vagrant/.ssh/authorized_keys
        chown -R vagrant /home/vagrant/.ssh
        ```
    - Update the box
        ```
        sudo apt update -y
        sudo apt upgrade -y
        ```
    - Ensure OpenSSH Server is installed
        ```
        apt install --yes openssh-server
        sudo sed -i /etc/ssh/sshd_config -e \
            "/#Author*/ c AuthorizedKeysFile %h/.ssh/authorized_keys"
        sudo service ssh restart
        ```
    - Install VirtualBox guest tools
        - `sudo apt install --yes gcc dkms build-essential linux-headers-$(uname -r)`
        - From the VM, select "Devices > Insert Guest Edition CD"
        - If needed, mount the CD from /dev/sr0
        - Run "VBoxLinuxAdditions.run" using sudo
    - At this point, make any further customizations and restart the VM
3. Create the Vagrant box from the VM
    - Ensure the VM is shut down before continuing
    - Create the "package.box" file which will hold the box
        - Create a folder to store the box file
        - Run `vagrant package --base {vm-name} --output {box-location}`
4. Create a metadata file
    - The metadata containing versioning information is stored as a simple json file.
    - It should begin with the following information:
    ```
    {
        "description": "Title of the Vagrant Box",
        "short_description": "Description of the Vagrant box",
        "name": "boxOwner/boxName",
        "versions": []
    }
    ```
    - Inside the "versions" block, the first entry can be added as follows:
    ```
    {
        "version": "1.0",
        "release_date": "dd-MMM-YYYY",
        "providers": [
            {
            "name": "virtualbox",
            "url": "file:///full/path/to/box",
            "checksum": "2d16e.....61ff3",
            "checksum_type": "sha256"
            }
        ]
    }
    ```
    - Each subsequent update to the box will require a new version block being added.
5. Test the box
    - Create a minimal vagrant file that references both:
        - `config.vm.box = "boxOwner/boxName"`
        - `config.vm.box_url = "file://box-metadata.json`
    - Run `vagrant up` to bring up the box, and add it to your local boxes.
    - At this point you can test the VM to ensure the box looks correct.