install:
	@chmod 644 /etc/sudoers
	@echo 'nfs ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
	@chmod 440 /etc/sudoers
	@cp -f /lib/exports_nfs /etc/exports
	@cp -f /lib/smb.conf /etc/samba/smb.conf
	@(echo 0000; echo 0000) | smbpasswd -a nfs -s
	@(echo 0000; echo 0000) | passwd nfs
