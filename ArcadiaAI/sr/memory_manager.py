class MemoryManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.storage_key = f"arcadia:memory:{user_id}"
        self.load()

    def load(self):
        raw = localStorage.getItem(self.storage_key)
        if not raw: 
            self.data = self.default_memory()
            return
        try:
            self.data = decrypt_if_needed(json.loads(raw))
        except:
            self.data = self.default_memory()

    def default_memory(self):
        return {
            "user": {},
            "conversations": {"frequent_topics": []},
            "system": {"memory_enabled": True, "version": "1.0"}
        }

    def update(self, path, value):
        if not self.is_enabled():
            return False
            
        set_nested(self.data, path, value)
        self.log_change("update", path, value)
        self.save()
        return True

    def get(self, path, default=None):
        if not self.is_enabled():
            return default
        return get_nested(self.data, path, default)

    def delete(self, key):
        if key in self.data["user"]:
            del self.data["user"][key]
        elif key in self.data["conversations"]:
            del self.data["conversations"][key]
        self.save()

    def save(self):
        data_to_save = self.data.copy()
        if self.data["system"]["encryption_enabled"]:
            data_to_save = encrypt(data_to_save)
        data_to_save["system"]["updated_at"] = datetime.now().isoformat()
        localStorage.setItem(self.storage_key, json.dumps(data_to_save))

    def is_enabled(self):
        return self.data["system"].get("memory_enabled", True)

    def log_change(self, action, key, value):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "key": key,
            "value_preview": str(value)[:50],
            "ip_hash": hash_ip(),  # opzionale
        }
        logs = json.loads(localStorage.getItem("arcadia:memory:log") or "[]")
        logs.append(log_entry)
        localStorage.setItem("arcadia:memory:log", json.dumps(logs[-100:]))  # ultimi 100

    def clear(self):
        localStorage.removeItem(self.storage_key)
        self.data = self.default_memory()
