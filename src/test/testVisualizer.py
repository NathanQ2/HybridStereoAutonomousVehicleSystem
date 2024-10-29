import socket


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 5006))

    dat = int.to_bytes(50, byteorder="big", signed=True)
    print(dat.hex())

    print("Listening for connection")
    sock.listen(1)
    conn, addr = sock.accept()

    print("Sending data")
    conn.send(dat)
    print("Sent")

    conn.close()
    sock.close()

    pass


if (__name__ == "__main__"):
    main()
