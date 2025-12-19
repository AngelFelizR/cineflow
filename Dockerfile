FROM ubuntu:24.04

# Updating the system
RUN apt update -y

# Installing packages to use, including 'xz-utils' for the Nix installer
RUN apt install curl openssh-server xz-utils -y

# The next line install Nix inside Docker
RUN bash -c 'sh <(curl --proto "=https" --tlsv1.2 -L https://nixos.org/nix/install) --daemon'

# Adds Nix to the path
ENV PATH="${PATH}:/nix/var/nix/profiles/default/bin"
ENV user=root

# Install direnv and nix-direnv for Positron integration
RUN nix-env -f '<nixpkgs>' -iA direnv nix-direnv

# Defining enviroment with Nix
COPY default.nix .

# We now build the environment
RUN nix-build

# Defining password for SSH 
RUN mkdir -p /var/run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
RUN echo 'root:sbs' | chpasswd

# Expose SSH port
EXPOSE 22

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]
