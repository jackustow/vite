class ViteError(Exception):
    pass


class ExtractionError(ViteError):
    pass


class TransformationError(ViteError):
    pass


class LoadError(ViteError):
    pass
