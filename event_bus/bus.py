""" A simple event bus """

from functools import wraps
from collections import defaultdict, Counter
from typing import Iterable, Callable, List, Dict, Any, Set, Union


class EventBus:
    """ A simple event bus class. """

    # ------------------------------------------
    #   Dunder Attrs
    # ------------------------------------------

    __slots__ = ('_events',)

    # ------------------------------------------
    #   Dunder Methods
    # ------------------------------------------

    def __init__(self) -> None:
        """ Creates new EventBus object. """

        self._events = defaultdict(set)  # type: Dict[Any, Set[Callable]]

    def __repr__(self) -> str:
        """ Returns EventBus string representation.

        :return: Instance with how many subscribed events.
        """
        return "<{}: {}>".format(self._cls_name(), self.event_count)

    def __str__(self) -> str:
        """ Returns EventBus string representation.

        :return: Instance with how many subscribed events.
        """

        return "{} subscribed events".format(self.event_count)

    # ==============================
    #  Properties.
    # ==============================

    @property
    def event_count(self) -> int:
        """ Sugar for returning total subscribed events.

        :return: Total amount of subscribed events.
        :rtype: int
        """
        return self.subscribed_event_count()

    # ------------------------------------------
    # Public Methods
    # ------------------------------------------

    def on(self, event: str) -> Callable:
        """ Decorator for subscribing a function to a specific event.

        :param event: Name of the event to subscribe to.
        :type event: str

        :return: The outer function.
        :rtype: Callable
        """

        def outer(func):
            self._events[event].add(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return outer

    def emit(self, event: str, *args, **kwargs) -> None:
        """ Emit an event and run the subscribed functions.

        :param event: Name of the event.
        :type event: str
        """
        for func in self.event_funcs(event):
            func(*args, **kwargs)

    def emit_only(self, event: str, func_names: Union[str, List[str]], *args,
                  **kwargs) -> None:
        """ Specifically only emits certain subscribed events.


        :param event: Name of the event.
        :type event: str

        :param func_names: Function(s) to emit.
        :type func_names: Union[ str | List[str] ]
        """
        if isinstance(func_names, str):
            func_names = [func_names]

        for func in self.event_funcs(event):
            if func.__name__ in func_names:
                func(*args, **kwargs)

    def emit_after(self, event: str) -> Callable:
        """ Decorator that emits events after the function is completed.

        :param event: Name of the event.
        :type event: str

        :return: Callable

        .. note:
            This plainly just calls functions without passing params into the
            subscribed callables. This is great if you want to do some kind
            of post processing without the callable requiring information
            before doing so.
        """

        def outer(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                returned = func(*args, **kwargs)
                self.emit(event)
                return returned

            return wrapper

        return outer

    def event_funcs(self, name: str) -> Iterable[Callable]:
        """ Returns an Iterable of the functions subscribed to a event.

        :param name: Name of the event.
        :type name: str

        :return: A iterable to do things with.
        :rtype: Iterable
        """
        for func in self._events[name]:
            yield func

    def event_func_names(self, name: str) -> List[str]:
        """ Returns string name of each function subscribed to an event.

        :param name: Name of the event.
        :type name: str

        :return: Names of functions subscribed to a specific event.
        :rtype: list
        """
        return [func.__name__ for func in self._events[name]]

    def subscribed_event_count(self) -> int:
        """ Returns the total amount of subscribed events.

        :return: Integer amount events.
        :rtype: int
        """
        event_counter = Counter()  # type: Dict[Any, int]

        for key, values in self._events.items():
            event_counter[key] = len(values)

        return sum(event_counter.values())

    def remove_subscriber(self, event: str, func_name: str) -> None:
        """ Removes a subscribed function from a specific event.

        :param event: The name of the event.
        :type event: str

        :param func_name: The name of the function to be removed.
        :type func_name: str

        :return:
        """
        event_funcs_copy = self._events[event].copy()

        for func in self.event_funcs(event):
            if func.__name__ == func_name:
                event_funcs_copy.remove(func)

        self._events[event] = event_funcs_copy

    # ------------------------------------------
    #   Private Methods
    # ------------------------------------------

    def _cls_name(self) -> str:
        """ Convenience method to reduce verbosity.

        :return: Name of class
        :rtype: str
        """
        return self.__class__.__name__
