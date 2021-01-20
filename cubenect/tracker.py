class ContactSlot:
    def __init__(self, slot):
        self.slot = slot

        self.center = None
        self.active = False
        self.was_freed = False # when the slot was just freed up 
                               # thus the multitouch driver might 
                               # need to kill the previous

    def squared_distance(self, candidate_new_center):
        l2_norm = (self.center[0] - candidate_new_center[0])**2 + \
                  (self.center[1] - candidate_new_center[1])**2
        return l2_norm

    def update_center(self, new_center):
        self.center = new_center

    def free(self):
        self.center = None
        self.active = False
        self.was_freed = True

    def new(self, center):
        self.center = center
        self.active = True

class ContactTracker:
    def __init__(self, max_slot=10, acceptance_radius=10):
        self.acceptance_radius2 = acceptance_radius**2

        self.max_slot = max_slot 
        self.slots = [ContactSlot(i) for i in range(self.max_slot)]
        self.currently_active_slots = set()
        self._possible_tracked_contacts = None
    
    def update(self, new_centers):
        self._possible_tracked_contacts = set(self.currently_active_slots)
        consider_adding_as_new = []

        # check if new candidates fit as an update
        # else try adding them as a new center
        # if the tracker can support more contacts
        for center in new_centers:
            if not self._update_currently_tracked(center):
                    consider_adding_as_new.append(center)

        # if some contacts wasn't updated then remove them...
        for i in list(self._possible_tracked_contacts):
            self.slots[i].free()
            self.currently_active_slots.remove(i)

        for center in consider_adding_as_new:
            empty_slots = set(range(self.max_slot)) - self.currently_active_slots
            
            if len(empty_slots) == 0:
                return # return from function because there are no empty slots left
                       # for the remaining new contacts
            
            self.slots[empty_slots[0]].new(center)
            self.currently_active_slots.add(empty_slots[0])

    def add_new(self, center):
        tracking_id = len(self.tracked_contacts) + 1
        self.tracked_contacts(Contact(center, tracking_id))

    def _update_currently_tracked(self, candidate_center):
        closest = None
        closest_dist = float('inf')

        # closest l2 norm instead of euclidean biparte matching
        for i in self._possible_tracked_contacts: 
            l2 = self.slots[i].squared_distance(candidate_center)
            if l2 < closest_dist:
                closest = i
                closest_dist = l2

        # using squared acceptance radius so rooting l2 norm is not necessary
        if closest_dist < self.acceptance_radius2:
            self.slots[closest].update_center(candidate_center)
            self._possible_tracked_contacts.remove(closest)
            return True
        
        return False # no previous contact accepted this as an update