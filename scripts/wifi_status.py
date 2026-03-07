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
    print(f"[-] {message} — halting")
    while True:
        time.sleep(10)


def wifi_status_message(wlan):
    """Return a human-readable string for the current WLAN status code."""
    code = wlan.status()
    return WIFI_STATUS.get(code, f"unknown error (code {code})")


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

        # Wait for connection up to CONNECT_TIMEOUT_S
        for _ in range(CONNECT_TIMEOUT_S * 2):
            if wlan.isconnected():
                break
            time.sleep(0.5)

        if not wlan.isconnected():
            status = wlan.status()
            reason = WIFI_STATUS.get(status, f"timed out (status {status})")
            print(f"[-] Connection failed: {reason}")
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
    env = load_env(".env")
    ssid = env.get("WIFI_SSID")
    password = env.get("WIFI_PASSWORD")

    if not ssid:
        halt("WIFI_SSID is missing or empty in .env")
    if not password:
        halt("WIFI_PASSWORD is missing or empty in .env")

    wlan = connect_wifi(ssid, password)
    print("[+] Connected!")

    while True:
        try:
            # Detect connection drop and reconnect
            if not wlan.isconnected():
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
