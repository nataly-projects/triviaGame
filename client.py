import socket
import chatlib

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5678


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    msg = chatlib.build_message(code, data)
    conn.send(msg.encode())


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket,
    then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


def connect():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER_IP, SERVER_PORT))
    pass
    return my_socket


def error_and_exit(error_msg):
    print(error_msg)
    exit()
    pass


def login(conn):
    while True:
        username = input("Please enter username: \n")
        password = input("enter your password: \n")
        msg = chatlib.join_data([username, password])
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], msg)
        cmd, data = recv_message_and_parse(conn)
        print("cmd :", cmd)
        print("data: ", data)
        if chatlib.PROTOCOL_SERVER["login_failed_msg"] != cmd:
            print("Logged in!")
            return


def build_send_recv_parse(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    return recv_message_and_parse(conn)


def get_score(conn):
    score_str, score = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["my_score"], "")
    print(str(score_str).lower() + " is : " + str(score))


def get_highscore(conn):
    score_str, score = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore"], "")
    print("High-score table:")
    print(score)


def play_question(conn):
    status, str = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_question"], "")
    if status == chatlib.PROTOCOL_SERVER["no_question"]:
        print("GAME-OVER")
        return
    else:
        print(status + " , " + str)
        arr = chatlib.split_data(str, 5)
        print("arr: ", arr)
        print(arr)
        print("Q: " + arr[1] + "?")
        print("    1. "+arr[2])
        print("    2. "+arr[3])
        print("    3. "+arr[4])
        print("    4. "+arr[5])
        res = input("Please choose an answer [1-4]: ")
        full_res = chatlib.join_data([arr[0], res])
        print(full_res)
        status, str = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer"], full_res)
        if status == chatlib.PROTOCOL_SERVER["wrong_answer"]:
            print("Nope, correct answer is " + str)
        else:
            print("YES!!!")


def get_logged_users(conn):
    status, str = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged"], "")
    print("Logged users: ")
    print(str)


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], '')


def main():
    s = connect()
    login(s)
    while True:
        choice = input("\ns     Get my score\nh     Get high score\np     Play a trivia question\nl     Get logged users\nq     Quit\nPlease enter your choice: ")
        if choice == 's':
            get_score(s)
        elif choice == 'h':
            get_highscore(s)
        elif choice == 'p':
            play_question(s)
        elif choice == 'l':
            get_logged_users(s)
        elif choice == 'q':
            logout(s)
            s.close()
            return


if __name__ == '__main__':
    main()
