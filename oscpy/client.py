import socket
from oscpy.parser import format_message, format_bundle
from time import sleep
from sys import platform

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_message(
    osc_address, values, ip_address, port, sock=SOCK, safer=False,
    encoding='', encoding_errors='strict'
):
    '''send an osc message to a a socket address.
    - osc address is the osc endpoint to send the data to (e.g b'/test')
      it should be a bytestring
    - values is the list of value to send, values can be any supported osc
      type (bytestring, float, int, blob...)
    - ip_address can either be an ip address if the used socket is of
      the AF_INET family, or a filename if the socket is of type AF_UNIX
    - port value will be ignored if socket is of type AF_UNIX
    - sock should be a socket object, the client's default socket can be
      used as default
    - the safer parameter allows to wait a little after sending, to make
      sure the message is actually sent before doing anything else,
      should only be useful in tight loop or cpu-busy code.
    - `encoding` if defined, will be used to encode/decode all
      strings sent/received to/from unicode/string objects, if left
      empty, the interface will only accept bytes and return bytes
      to callback functions.
    - `encoding_errors` if `encoding` is set, this value will be
      used as `errors` parameter in encode/decode calls.

    examples:
        send_message(b'/test', [b'hello', 1000, 1.234], 'localhost', 8000)
        send_message(b'/test', [], '192.168.0.1', 8000, safer=True)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_message(b'/test', [], '192.168.0.1', 8000, sock=sock, safer=True)

        # unix sockets works on linux and osx, and over unix platforms,
        # but not windows
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        send_message(b'/some/address', [1, 2, 3], b'/tmp/sock')

    '''
    if platform != 'win32' and sock.family == socket.AF_UNIX:
        address = ip_address
    else:
        address = (ip_address, port)
    sock.sendto(
        format_message(
            osc_address, values, encoding=encoding,
            encoding_errors=encoding_errors
        ),
        address
    )
    if safer:
        sleep(10e-9)


def send_bundle(
    messages, ip_address, port, timetag=None, sock=None, safer=False,
    encoding='', encoding_errors='strict'
):
    '''send a bundle built from the `messages` iterable.
    each item in the `messages` list should be a two-tuple of the form:
    (address, values).

    example:
        (
            ('/create', ['name', 'value']),
            ('/select', ['name']),
            ('/update', ['name', 'value2']),
            ('/delete', ['name']),
        )

    timetag is optional but can be a float of the number of seconds
    since 1970 when the events described in the bundle should happen.

    See `send_message` documentation for the other parameters.
    '''
    if not sock:
        sock = SOCK
    sock.sendto(
        format_bundle(
            messages, timetag=timetag, encoding=encoding,
            encoding_errors=encoding_errors
        ),
        (ip_address, port),
    )
    if safer:
        sleep(10e-9)


class OSCClient(object):
    '''Class wrapper for the send_message and send_bundle functions,
    allowing to define address, port and sock parameters for all
    calls. If encoding is provided, all string values will be encoded
    into this encoding before being sent.
    '''
    def __init__(
        self, address, port, sock=None, encoding='', encoding_errors='strict'
    ):
        self.address = address
        self.port = port
        self.sock = sock or SOCK
        self.encoding = encoding
        self.encoding_errors = encoding_errors

    def send_message(self, address, values, safer=False):
        send_message(
            address, values, self.address, self.port, self.sock,
            safer=safer, encoding=self.encoding,
            encoding_errors=self.encoding_errors
        )

    def send_bundle(self, messages, timetag=None, safer=False):
        send_bundle(
            messages, self.address, self.port, timetag=timetag,
            sock=self.sock, safer=safer, encoding=self.encoding,
            encoding_errors=self.encoding_errors
        )
