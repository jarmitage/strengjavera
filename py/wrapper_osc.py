from iipyper import OSC, OSCMap

class OSCWrapper:
    def __init__(self, host_ip, client_ip, receive_port, send_port, name, create_patch=True, patch_type="Pd"):
        self.host_ip = host_ip
        self.client_ip = client_ip
        self.receive_port = receive_port
        self.send_port = send_port
        self.name = name
        self.create_patch = create_patch
        self.patch_type = patch_type
        self.host = OSC(self.host_ip, self.receive_port, verbose=True, concurrent=True)
        self.host.create_client(self.name, self.client_ip, self.send_port)
        self.map = OSCMap(self.host, self.name, create_patch=self.create_patch, patch_type=self.patch_type, patch_filepath=self.name)
