# models.py
# (Future use ke liye – structure reference)

# models.py (reference only)

class User:
    def __init__(self, name, email, verified=False):
        self.name = name
        self.email = email
        self.verified = verified


class LostItem:
    def __init__(self, email, description):
        self.email = email
        self.description = description


class FoundItem:
    def __init__(self, description, location):
        self.description = description
        self.location = location