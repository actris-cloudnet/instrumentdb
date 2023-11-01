from .version import __version__


def version(request):
    return {"INSTRUMENTS_VERSION": __version__}
