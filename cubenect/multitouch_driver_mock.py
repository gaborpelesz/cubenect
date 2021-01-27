class MultitouchDriverMock:
    def __init__(self):
        self.current_commands = None 

    def freeup_slot(self, slot_id):
        self.current_commands.append(f"Free up slot: {slot_id}")

    def activate_slot(self, slot_id):
        self.current_commands.append(f"Lock slot: {slot_id}")

    def move(self, slot_id, center):
        self.current_commands.append(f"slot {slot_id}: move -> ({center[0]}, {center[1]})")

    def print_action_callback(self, contact_tracker):
        self.current_commands = []
        for slot_id in range(len(contact_tracker.slots)):
            if contact_tracker.slots[slot_id].was_freed:
                self.freeup_slot(slot_id)
                contact_tracker.slots[slot_id].was_freed = False
            if contact_tracker.slots[slot_id].activate:
                self.activate_slot(slot_id)
                contact_tracker.slots[slot_id].activate = False
            if not contact_tracker.slots[slot_id].center is None:
                self.move(slot_id, contact_tracker.slots[slot_id].center)
        self.send_commands()

    def send_commands(self):
        if len(self.current_commands) > 0:
            print('\n'.join(self.current_commands))
