import itertools


def batched(iterable, batch_size: int):
    """Yield successive batch_size-sized chunks from an iterable."""
    it = iter(iterable)
    while batch := list(itertools.islice(it, batch_size)):
        yield batch