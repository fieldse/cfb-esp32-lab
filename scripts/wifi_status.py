import network
import time


# MicroPython WLAN status codes
WIFI_STATUS = {
    200: "beacon timeout (AP not responding)",
    201: "SSID not found",
    202: "wrong password",
    203: "association failed",
    204: "handshake timeout",
}

CONNECT_TIMEOUT_S  = 20
DHCP_TIMEOUT_S     = 5
RETRY_DELAY_S      = 30
STATUS_INTERVAL_S  = 5


def load_env(path=".env"):
    """Parse a simple KEY=VALUE .env file, ignoring comments and blank lines."""
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
    return env


def halt(message):
    """Print an error and idle forever to avoid soft reboot loops."""
    while True:
        print(f"[-] {message} — process halted")
        time.sleep(2)


def wifi_status_message(wlan):
    """Return a human-readable string for the current WLAN status code."""
    code = wlan.status()
    return WIFI_STATUS.get(code, f"unknown error (code {code})")

def load_envs():
    """Load WiFi SSID and password from .env file. Halts if either is missing."""
    env = load_env(".env")
    ssid = env.get("WIFI_SSID")
    password = env.get("WIFI_PASSWORD")
    if not ssid:
        halt("WIFI_SSID is missing or empty in .env")
    if not password:
        halt("WIFI_PASSWORD is missing or empty in .env")
    return ssid, password


def connect_wifi(ssid, password):
    """
    Connect to WiFi. Retries indefinitely with RETRY_DELAY_S between attempts.
    Returns the connected WLAN interface.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    while True:
        if wlan.isconnected():
            return wlan

        print(f"[+] Connecting to {ssid}...")
        wlan.connect(ssid, password)

        # Wait for isconnected() up to CONNECT_TIMEOUT_S
        for _ in range(CONNECT_TIMEOUT_S * 2):
            if wlan.isconnected():
                break
            print(".", end="", flush=True)
            time.sleep(0.5)
        print()
        print(f"[.] isconnected: {wlan.isconnected()}")

        # Wait for status() == 1001 (STAT_GOT_IP) — ESP32-C6 can lag behind isconnected()
        for _ in range(CONNECT_TIMEOUT_S * 2):
            if wlan.status() == 1001:
                break
            print(".", end="", flush=True)
            time.sleep(0.5)
        print()
        print(f"[.] status: {wlan.status()}")

        if not wlan.isconnected() and wlan.status() != 1001:
            status = wlan.status()
            reason = WIFI_STATUS.get(status, "unknown error")
            print(f"[-] Connection failed: {reason} (status {status})")
            print(f"[+] Retrying in {RETRY_DELAY_S}s...")
            wlan.disconnect()
            time.sleep(RETRY_DELAY_S)
            continue

        # Wait for DHCP to assign a real IP
        print("[+] Waiting for IP address...")
        for _ in range(DHCP_TIMEOUT_S * 2):
            ip = wlan.ifconfig()[0]
            if ip != "0.0.0.0":
                break
            time.sleep(0.5)

        if wlan.ifconfig()[0] == "0.0.0.0":
            print("[-] DHCP timed out — retrying connection...")
            wlan.disconnect()
            time.sleep(RETRY_DELAY_S)
            continue

        return wlan


def main():
    print(f"========= Wifi connecting ========\n")
    ssid, password = load_envs()

    wlan = connect_wifi(ssid, password)
    print("[+] Connected!")

    while True:
        try:
            # Detect connection drop and reconnect
            if not wlan.isconnected() and wlan.status() != 1001:
                print("[-] Connection lost — reconnecting...")
                wlan = connect_wifi(ssid, password)
                print("[+] Reconnected!")

            ip, subnet, gateway, dns = wlan.ifconfig()
            print(f"SSID: {ssid}  |  IP: {ip}  |  Gateway: {gateway}")

        except Exception as e:
            print(f"[-] Error: {e}")

        time.sleep(STATUS_INTERVAL_S)


if __name__ == "__main__":
    main()
