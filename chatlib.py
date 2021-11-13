# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "my_score": "MY_SCORE",
    "highscore": "HIGHSCORE",
    "get_question": "GET_QUESTION",
    "send_answer": "SEND_ANSWER",
    "logged": "LOGGED"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR",
    "no_question": "NO_QUESTIONS",
    "your_question": "YOUR_QUESTION",
    "correct_answer": "CORRECT_ANSWER",
    "wrong_answer": "WRONG_ANSWER",
    "logged_answer": "LOGGED_ANSWER",
    "error_msg": "ERROR",
    "your_score": "YOUR_SCORE",
    "all_score": "ALL_SCORE"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if error occured
    """
    full_msg = ""
    length = str(len(data))
    #cmd == 'LOGIN' and

    #print("the msg_len rjust: " + msg_len)

    if len(data) <= MAX_DATA_LENGTH and len(cmd) <= CMD_FIELD_LENGTH:
        msg_len = length.rjust(4, "0")
    #    if len(data) <=9:
    #        msg_len = '000'+ str(len(data))
    #    elif len(data) <=99:
    #        msg_len = '00' + str(len(data))
    #    elif len(data) <=999:
    #        msg_len = '0' + str(len(data))
        full_msg = cmd.ljust(CMD_FIELD_LENGTH) + DELIMITER + msg_len + DELIMITER + data
    else:
        full_msg = None
    return full_msg


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    cmd = None
    msg = None
    c = data.count(DELIMITER)
    if c == 2:
        arr = data.split(DELIMITER)
        if arr[1].strip().isdigit() and 0 <= int(arr[1]) <= MAX_MSG_LENGTH and len(arr[2]) == int(arr[1]):
            msg = arr[2]
            cmd = arr[0].strip()

    return cmd, msg


def split_data(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's data field delimiter (|#) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    c = msg.count(DATA_DELIMITER)
    if c != expected_fields:
        return 'None'
    else:
        arr = msg.split(DATA_DELIMITER)
    return arr


def join_data(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter.
    Returns: string that looks like cell1#cell2#cell3
    """
    return DATA_DELIMITER.join(msg_fields)


def main():
    print(join_data(['username' , 'password']))
    print(join_data(["question" , "ans1" , "ans2" , "ans3" , "ans4" , "correct"]))
    print(split_data("username#password" , 1))
    print(split_data("user#name#pass#word", 2))
    print(split_data("username" , 2))
    print(build_message("LOGIN", "aaaa#bbbb"))
    print(build_message("LOGIN", "aaaabbbb"))
    print(build_message("0123456789ABCDEFG", ""))
    print(build_message("A", "A" * (MAX_DATA_LENGTH + 1)))
    print(build_message("LOGIN", ""))
    print(parse_message("LOGIN           |   9|aaaa#bbbb"))
    print(parse_message("LOGIN           |	  z|data"))
    print(parse_message("LOGIN           |   4|data"))


if __name__ == '__main__':
    main()
