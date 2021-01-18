def send(commands):
    #print("Running:", commands)
    if type(commands) == list:
        commands = "\n".join(commands)
    with open("/dev/virtual_touchscreen", "w") as f:
        f.write(commands)

def packet(commands, slot_id=None):
    if not slot_id is None:
        return [f"s {slot_id}"] + commands + ["S 0\n"]
    return commands + ["S 0\n"]

def move(x, y):
    return [f"X {x}", f"Y {y}", f"x {x}", f"y {y}", "a 1"]

def touch(t_id):
    return [f"T {t_id}", "0 10", ": 100", "e 0", "d 0"]

def untouch():
    return ["T -1", "0 0", ": 0", "e 0", "u 0"]