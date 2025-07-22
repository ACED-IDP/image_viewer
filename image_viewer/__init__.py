import indexclient.client


def monkey_patch_indexclient__get():
    """Monkey patch IndexClient._get to ensure 'auth' is set and log calls."""
    original__get = indexclient.client.IndexClient._get

    def patched__get(self, *args, **kwargs):
        """Patch to ensure 'auth' is set and log the call."""
        if 'auth' not in kwargs:
            kwargs['auth'] = self.auth
        return original__get(self, *args, **kwargs)

    indexclient.client.IndexClient._get = patched__get


# main
monkey_patch_indexclient__get()
