from concurrent.futures import ThreadPoolExecutor
from typing import Callable


def func_wrapper(args):
    (f, offset, *args) = args
    items = f(*args)
    return [(i + offset, item) for i, item in enumerate(items)]


def get_items(
    func: Callable,
    *args,
    parse: Callable = lambda _: _,
    chunk_size: int = 100,
    processes: int = 5,
):
    """
    This function performs pagination on a function that supports
    `limit`/`offset` parameters and it runs API requests in parallel to speed
    things up.
    """
    items = []
    offsets = [-chunk_size]
    remaining = chunk_size * processes

    with ThreadPoolExecutor(
        processes, thread_name_prefix=f'mopidy-tidal-{func.__name__}-'
    ) as pool:
        while remaining == chunk_size * processes:
            offsets = [offsets[-1] + chunk_size * (i + 1) for i in range(processes)]

            pool_results = pool.map(
                func_wrapper,
                [
                    (
                        func,
                        offset,
                        *args,
                        chunk_size,  # limit
                        offset,  # offset
                    )
                    for offset in offsets
                ],
            )

            new_items = []
            for results in pool_results:
                new_items.extend(results)

            remaining = len(new_items)
            items.extend(new_items)

    items = sorted([_ for _ in items if _], key=lambda item: item[0])
    sorted_items = [item[1] for item in items]
    return list(map(parse, sorted_items))
