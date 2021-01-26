with open("/etc/gdm3/custom.conf", "r") as f:
    conf_raw = f.read()

import os
USER = os.environ['SUDO_USER']

try:
    conf_raw.index(f"AutomaticLogin={USER}")
    print(f"Automatic login already enabled for '{USER}'")

except ValueError as e:
    insert_autologin_rule = f"\nAutomaticLoginEnable=True\nAutomaticLogin={USER}\n"
    daemon = "[daemon]"
    insertion_index = conf_raw.index(daemon) + len(daemon)
    conf_raw_updated = conf_raw[:insertion_index] + insert_autologin_rule + conf_raw[insertion_index:]
    with open("/etc/gdm3/custom.conf", "w") as f:
        f.write(conf_raw_updated)

