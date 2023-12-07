class Document:

    def __init__(self, content: str = ""):
        self._content = content

    def insert_at(self, char, idx):
        if len(char) != 1:
            raise Exception("Character should be inserted")
        if idx not in range(0, len(self._content) + 1):
            raise Exception(f"insert {char} at {idx} - Index out of bound on '{self._content}'")
        self._content = self._content[:idx] + char + self._content[idx:]

    def delete_at(self, idx):
        if idx not in range(0, len(self._content)):
            raise Exception(f"delete at {idx} - Index out of bound on '{self._content}'")
        char = self._content[idx]
        assert len(char) == 1
        self._content = self._content[:idx] + self._content[idx + 1:]
        return char

    def get_content(self):
        return self._content
