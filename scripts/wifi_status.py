import network
import time
import gc
import machine
import socket

# MicroPython WLAN status codes
WIFI_STATUS = {
    200: "beacon timeout (AP not responding)",
    201: "SSID not found",
    202: "wrong password",
    203: "association failed",
    204: "handshake timeout",
    1001: "connected (got IP)",
}

CONNECT_TIMEOUT_S = 20
DHCP_TIMEOUT_S    = 5
RETRY_DELAY_S     = 30
STATUS_INTERVAL_S = 5
MAX_RETRIES       = 5


class WifiManager:

    def __init__(self):
        self.ssid     = None
        self.password = None
        self.wlan     = network.WLAN(network.STA_IF)

    def load_env(self, path=".env"):
        """Parse .env and store SSID and password on self."""
        env = {}
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, _, value = line.partition("=")
                    env[key.strip()] = value.strip()
        except OSError:
            print(f"[-] Could not read {path}")
            return False

        self.ssid     = env.get("WIFI_SSID")
        self.password = env.get("WIFI_PASSWORD")

        print(f"[.] SSID:     {repr(self.ssid)}")
        print(f"[.] Password: {repr(self.password)}")
        return bool(self.ssid and self.password)

    def reset_interface(self):
        """Cycle the WiFi interface off and on to clear internal state."""
        print("[+] Resetting WiFi interface...")
        # Clear the previous connections
        network.WLAN(network.AP_IF).active(False)  # Disable AP interface
        self.wlan.active(False)
        time.sleep(3)
        self.wlan.active(True)

        print("[+] Interface ready")

    def connect(self):
        """Attempt a single connection using stored SSID and password."""
        if not self.ssid or not self.password:
            print("[-] No credentials loaded — call load_env() first")
            return False

        print(f"[+] Connecting to {self.ssid}...")
        gc.collect()                                # Ensure adequate heap memory
        network.WLAN(network.AP_IF).active(False)   # Disable AP interface
        self.wlan.config(pm=self.wlan.PM_NONE)      # Disable power management
        self.wlan.config(reconnects=0)              # Manual retry control

        # Connect
        self.wlan.connect(self.ssid, self.password)
        for _ in range(CONNECT_TIMEOUT_S * 2):
            if self.wlan.status() == 1001:
                break
            print(".", end="")
            time.sleep(0.5)
        print()

        print(f"[.] isconnected: {self.wlan.status() == 1001}")
        print(f"[.] status:      {self.wlan.status()} ({WIFI_STATUS.get(self.wlan.status(), 'unknown')})")
        return self.wlan.status() == 1001

    def wait_for_ip(self):
        """Wait for DHCP to assign a non-zero IP address."""
        print("[+] Waiting for IP...")
        for _ in range(DHCP_TIMEOUT_S * 2):
            ip = self.wlan.ifconfig()[0]
            if ip != "0.0.0.0":
                print(f"[+] IP assigned: {ip}")
                return True
            time.sleep(0.5)
        print("[-] DHCP timed out")
        return False

    def status(self):
        """Print current connection state, IP info, and WLAN status code."""
        code = self.wlan.status()
        print(f"[.] connected:   {code == 1001}  (isconnected() unreliable on ESP32-C6, using status)")
        print(f"[.] status:      {code} ({WIFI_STATUS.get(code, 'unknown')})")
        if self.wlan.status() == 1001:
            ip, subnet, gateway, dns = self.wlan.ifconfig()
            print(f"[.] SSID:        {self.ssid}")
            print(f"[.] IP:          {ip}")
            print(f"[.] Subnet:      {subnet}")
            print(f"[.] Gateway:     {gateway}")
            print(f"[.] DNS:         {dns}")

    def connect_with_retry(self, max_retries=MAX_RETRIES):
        """
        Full connection flow with retries.
        Cycles interface, connects, waits for IP. Retries on failure.
        """
        for attempt in range(max_retries):
            print(f"connection attempt #{attempt}")
            self.reset_interface()
            if self.connect():
                if self.wait_for_ip():
                    return self.wlan.ifconfig()
            print(f"[+] Retrying in {RETRY_DELAY_S}s...")
            self.wlan.disconnect()
            time.sleep(RETRY_DELAY_S)
        # We've failed to get there: machine reset
        print("[-] connection failed -- resetting device")
        machine.reset()

    def ping(self, host="8.8.8.8", port=53, timeout=3):
        """Test network reachability by opening a TCP socket to host:port.
        Defaults to Google DNS (8.8.8.8:53) — no HTTP needed.
        Returns True if reachable, False otherwise."""
        print(f"[.] Pinging {host}:{port}...")
        try:
            addr = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect(addr)
            s.close()
            print(f"[+] Reachable: {host}:{port}")
            return True
        except OSError as e:
            print(f"[-] Unreachable: {host}:{port} — {e}")
            return False

    def run(self):
        """Load env, connect, then print status on repeat."""
        if not self.load_env():
            print("[-] Missing credentials — halting")
            while True:
                time.sleep(10)

        self.connect_with_retry()
        print("[+] Connected!")

        while True:
            try:
                if not self.wlan.status() == 1001:
                    print("[-] Connection lost — reconnecting...")
                    self.connect_with_retry()
                    print("[+] Reconnected!")
                self.status()
            except Exception as e:
                print(f"[-] Error: {e}")
            time.sleep(STATUS_INTERVAL_S)


# Uncomment to run automatically on boot:
# wifi = WifiManager()
# wifi.run()
