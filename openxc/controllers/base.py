"""Contains the abstract interface for sending commands back to a vehicle
interface.
"""
import numbers

from openxc.formats.json import JsonFormatter


class Controller(object):
    """A Controller is a physical vehicle interface that accepts commands to be
    send back to the vehicle. This class is abstract, and implemtnations of the
    interface must define at least the ``write_bytes``, ``version``, or
    ``reset`` methods.
    """

    def write(self, name, value):
        """Format the given signal name and value into an OpenXC write request
        and write it out to the controller interface as bytes, ending with a
        \0 character.
        """
        value = self._massage_write_value(value)
        message = JsonFormatter.serialize({'name': name, 'value': value})
        bytes_written = self.write_bytes(message + "\x00")
        assert bytes_written == len(message) + 1
        return bytes_written

    def write_raw(self, message_id, data):
        """Format the given CAN ID and data into a JSON message
        and write it out to the controller interface as bytes, ending with a
        \0 character.

        TODO this could write to a separate USB endpoint that is expecting
        raw-style JSON messages.
        """
        if not isinstance(message_id, numbers.Number):
            try:
                message_id = int(message_id, 0)
            except ValueError:
                raise ValueError("ID and data must be numerical")
        if not isinstance(data, numbers.Number):
            try:
                data = int(data, 0)
            except ValueError:
                raise ValueError("ID and data must be numerical")

        message = JsonFormatter.serialize({'id': message_id, 'data': data})
        bytes_written = self.write_bytes(message + "\x00")
        assert bytes_written == len(message) + 1
        return bytes_written

    def write_bytes(self, data):
        """Write the bytes in ``data`` out to the controller interface."""
        raise NotImplementedError("Don't use Controller directly")

    def version(self):
        """Request and return the version of the vehicle interface."""
        raise NotImplementedError("%s cannot be used with control commands" %
                type(self).__name__)

    def reset(self):
        """Reset the vehicle interface."""
        raise NotImplementedError("%s cannot be used with control commands" %
                type(self).__name__)

    @classmethod
    def _massage_write_value(cls, value):
        """Convert string values from command-line arguments into first-order
        Python boolean and float objects, if applicable.
        """
        if value == "true":
            value = True
        elif value == "false":
            value = False
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        return value


class ControllerError(Exception):
    pass
