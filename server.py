##############################################################################
# server.py
##############################################################################

import socket
import chatlib
import random
import select
import json
import requests


# GLOBALS
users = {}
questions = {}
logged_users = {}
messages_to_send = []

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    global messages_to_send
    full_msg = chatlib.build_message(code, msg)
    messages_to_send.append((conn, full_msg))
    print("messages_to_send: ", messages_to_send)
    # conn.send(full_msg.encode())
    print("[SERVER] ", full_msg)  # Debug print


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
    print("[CLIENT] ", full_msg)  # Debug print
    return cmd, data


def print_client_socket(client_socket):
    for c in client_socket:
        print("\t", c.getpeername())


# Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    global questions
    with open("questions.txt", "r") as c_file:
        line = c_file.read()
        questions = json.loads(line)
    return questions

def load_questions_from_web():
    global questions
    query = {'amount': 50, 'type': 'multiple'}
    count = 1
    response = requests.get('https://opentdb.com/api.php/', params=query)
    print(response.text)
    p = json.loads(response.text)
    ques_arr = p['results']
    for q in ques_arr:
        questions[count] = q
        count = count + 1
    print(questions)
    return questions

def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    global users
    with open("users.txt", "r") as c_file:
        line = c_file.read()
        users = json.loads(line)
    return users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    # Implement code ...
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen()
    return sock


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["error_msg"], error_msg)


##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
    global users
    print("in get score")
    print(username)
    if username in users:
        val = users[username]
        score = val['score']
        print("score: ", score)
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_score"], str(score))


def handle_highscore_message(conn):
    global users
    scores = {}
    msg = ""
    for username in users:
        val = users[username]
        scores[username] = val['score']
    print(scores)
    for k in sorted(scores, key=scores.get, reverse=True):
        msg = msg + str(k) + ": " + str(scores[k]) + "\n"
        print(msg)
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score"], msg)


def handle_logged_message(conn):
    logged = ""
    for user in logged_users:
        logged = logged + logged_users[user] + ", "
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER['logged_answer'], logged)


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    del logged_users[conn.getpeername()[1]]
    conn.close()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users
    arr = chatlib.split_data(data, 1)
    print("arr in handle login: ", arr)
    if str(arr[0]) in users:
        val = users[arr[0]]
        if arr[1] == val['password']:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], "")
            logged_users[conn.getpeername()[1]] = arr[0]
            print(logged_users)
        else:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], "Password does not match!")
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], "Username does not exists")


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users
    print("cmd: ", cmd)
    print (conn.getpeername())
    if conn.getpeername()[1] not in logged_users:
        if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
            handle_login_message(conn, data)
    else:
        if cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
            handle_logout_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["my_score"]:
            print("in handle_client_message in my score")
            handle_getscore_message(conn, logged_users[conn.getpeername()[1]])
        elif cmd == chatlib.PROTOCOL_CLIENT["highscore"]:
            handle_highscore_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["logged"]:
            handle_logged_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["get_question"]:
            handle_question_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["send_answer"]:
            handle_answer_message(conn, logged_users[conn.getpeername()[1]], data)


def create_random_question(username):
    global questions
    global users
    msg = ""
    count = len(questions)
    num = random.randint(1, count)
    ask_question = users[username]['questions_asked']
    print("ask_question: ", ask_question)
    if count == len(ask_question):
        return msg
    else:
        while num in ask_question:
            num = random.randint(0, count - 1)
        print("random num: ", num)
        ques = questions[num]
        print("ques: ", ques)
        ask_question.append(num)
        msg = msg + str(num) + chatlib.DATA_DELIMITER + str(ques['question'])
        answer_arr = ques['incorrect_answers']
        answer_arr.append(ques['correct_answer'])  # TODO - The correct answer always in 4
        for item in answer_arr:
            msg = msg + chatlib.DATA_DELIMITER + item
        print("ques msg: ", msg)
        return msg


def handle_question_message(conn):
    global logged_users
    ques = create_random_question(logged_users[conn.getpeername()[1]])
    cmd = ""
    if ques == "":
        cmd = chatlib.PROTOCOL_SERVER['no_question']
    else:
        cmd = chatlib.PROTOCOL_SERVER["your_question"]
    build_and_send_message(conn, cmd, ques)


def handle_answer_message(conn, username, data):
    global questions
    global users
    arr = chatlib.split_data(data, 1)
    key = questions[int(arr[0])]
    cmd = ""
    msg = ""
    if str(arr[1]) == str(4):  # correct # TODO - The correct answer always 4. The user send the number of the correct ques, but in the dict is the str answer.
        val = users[username]
        val['score'] = val['score'] + 5
        cmd = chatlib.PROTOCOL_SERVER["correct_answer"]
    else:  # wrong
        cmd = chatlib.PROTOCOL_SERVER["wrong_answer"]
        msg = str(questions[int(arr[0])]['correct_answer'])
    build_and_send_message(conn, cmd, msg)

# TODO- save the score in the users.txt
def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions
    global messages_to_send
    users = load_user_database()
    questions = load_questions_from_web()
    print("users: ", users)
    print("questions: ", questions)
    client_sockets = []

    server_socket = setup_socket()
    print("Welcome to Trivia Server!")
    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, [], [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                (client_socket, client_address) = server_socket.accept()
                client_sockets.append(client_socket)
                print("New client joined! ", client_address)

                print_client_socket(client_sockets)
            else:
                print("New data from client")
                cmd, data = recv_message_and_parse(current_socket)
                handle_client_message(current_socket, cmd, data)
                if cmd == chatlib.PROTOCOL_CLIENT["logout_msg"] or cmd is None or cmd == "":
                    print("Connection closed")
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    print_client_socket(client_sockets)
        print("messages_to_send: ", messages_to_send)
        for item in messages_to_send:
            item[0].send(str(item[1]).encode())
            messages_to_send.remove(item)


if __name__ == '__main__':
    main()
