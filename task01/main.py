import sys
import os

MAX_ARGC_NUM = len(["-f", "file.txt", "-d", "dir", "-n", "100", "-l", "-r", "some"]) + 1
MIN_ARGC_NUM = len(["-f", "file.txt"]) + 1
TEG_START_SYM = "@"
TEG_FINISH_SYM = ":"
NEW_SCORE_LINE_START = "- Новый score пользователя @"
NEW_SCORE_LINE_FINISH = "\n"
DEFAULT_SUBSTRING_SIZE: int = 200


def main(argc: list[str]) -> int:
    f_name: str = required_argc(argc)
    flags: dict = optional_argc(argc)
    print(flags)

    with open(f_name, "r", encoding="utf_8_sig") as file_stream:
        f_str = file_stream.read()

    if len(f_str) < flags["n"]:
        print(f"WARNING: -n {flags['n']} longer then string size {len(f_str)}")
        print(f"Will parse by default size {DEFAULT_SUBSTRING_SIZE}")
        flags["n"] = DEFAULT_SUBSTRING_SIZE

    undiv_strings: dict = create_undiv_str_dict(f_str, flags)

    parsed_strings: list[str] = parse_string(f_str, flags["n"], undiv_strings)
    print_substrings(parsed_strings, flags["d"])
    return 0


# check -f file_name.txt in argc
def required_argc(argc: list[str]) -> str:
    if len(argc) < MIN_ARGC_NUM or len(argc) > MAX_ARGC_NUM:
        exit_error("wrong number of command line arguments")
    file_name: str = check_txt_str(str(find_msg_after_flag("-f", argc)))
    if not file_name:
        exit_error("Expect -f file_name.txt in command line")
    return file_name


def check_txt_str(file_name: str) -> str | None:
    if not file_name:
        return None
    if not file_name.endswith(".txt"):
        exit_error("invalid file type require .txt file")
    return file_name


# return msg after -flag
def find_msg_after_flag(flag: str, argc: list[str]) -> str | None:
    try:
        flag_pos = argc.index(flag)
    except ValueError:
        return None
    if flag_pos == len(argc) - 1:  # flag is last argument no msg after flag
        return exit_error("invalid command line flags")
    else:
        return argc[flag_pos + 1]


# find optional -flags in argc
def optional_argc(argc: list[str]) -> dict:
    flags: dict = {"n": find_msg_after_flag("-n", argc), "d": find_msg_after_flag("-d", argc),
                   "r": find_msg_after_flag("-r", argc), "l": True if "-l" in argc else False}
    if is_unexpected_flags(len(argc), flags):
        exit_error("unknown flags in command line arguments\nExpect: -f, -r, -n, -d, -l")
    # default value if no -n
    flags["n"]: int = int(flags["n"]) if flags["n"] else DEFAULT_SUBSTRING_SIZE
    return flags


# cmp expected and received flags return false if vals not eq
def is_unexpected_flags(argc_list_len: int, read_flags: dict) -> bool:
    receive_argc = MIN_ARGC_NUM
    for it in read_flags:
        if it == "l":  # flag without post msg
            receive_argc += 1 if True is read_flags[it] else 0
            continue
        if read_flags[it]:
            receive_argc += 2
    if receive_argc != argc_list_len:
        return True
    return False


# return dictionary of undivided parts of string "@Kek Chel" [indx(@)] = indx(l)
def create_undiv_str_dict(string: str, flags: dict) -> dict:
    undiv_str_indx: dict = {}
    string_shift: int = 0
    while True:
        start_indx, finish_indx = find_undivided_part(string[string_shift:len(string)], flags)
        if start_indx == -1 or finish_indx == -1:
            break
        undiv_str_indx[start_indx + string_shift] = finish_indx + string_shift
        string_shift += finish_indx
    return undiv_str_indx


# from @ to :, if -l from Новый Score to \n
def find_undivided_part(string: str, flags: dir) -> tuple[int, int]:
    at_indx: int = string.find(TEG_START_SYM)  # at = @
    score_indx: int = string.find(NEW_SCORE_LINE_START) if flags["l"] else len(string)
    if at_indx < score_indx:  # find @ first
        return at_indx, string.find(TEG_FINISH_SYM, at_indx)
    else:  # find Новый Score first
        return score_indx, string.find(NEW_SCORE_LINE_FINISH, score_indx)


# return left border of undivided line if position_in_str is in undivided line
def get_undiv_str_border(undiv_strings: dict, position_in_str: int) -> int:
    for it in undiv_strings:
        if undiv_strings[it] > position_in_str > it:
            return it
    return position_in_str


def get_left_space(string: str, indx: int) -> int:
    if indx == len(string):
        return indx
    elif string[indx].isspace():
        return indx
    else:
        return max(string.rfind("\n"), string.rfind("\t"), string.rfind(" "),
                   string.rfind("\f"), string.rfind("\r"), string.rfind("\v"))


def get_right_border(string: str, undiv_strings: dict, prev_border: int, subline_size: int) -> int:
    right_border: int = get_undiv_str_border(undiv_strings, prev_border)
    new_border: int = get_left_space(string[0:right_border + 1], right_border)
    # + 1 to save space symbols in previous line
    return new_border + 1 if new_border != subline_size else new_border  # cannot put space in prev line


# kind of magic
def parse_string(string: str, subline_size: int, undiv_strings: dict) -> list[str]:
    parsed_strings: list[str] = []
    right_border: int = 0

    while right_border < len(string) - 1:

        left_border: int = right_border
        if len(string) < (right_border := right_border + subline_size):
            right_border = len(string)

        right_border = get_right_border(string, undiv_strings, right_border, subline_size)

        if right_border == left_border:
            if string[right_border:len(string)].isspace() or len(string) - right_border > subline_size:  # hack
                exit_error(f"Cannot parce line. Undivided parts longer then -n {subline_size}")
            else:  # no space in the end of file
                right_border = len(string)

        parsed_strings.append(string[left_border:right_border])

    return parsed_strings


# Just print substrings to command line and files is required
def print_substrings(sub_strings: list[str], new_dir: str) -> None:
    for indx, string in enumerate(sub_strings):  # to command line
        print(f"\nSubstring #{indx + 1} len = {len(string)}\n{string}")
    if not new_dir:  # if require
        return

    new_dir: str = os.path.join(os.getcwd(), new_dir)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    for indx, string in enumerate(sub_strings):
        with open(os.path.join(new_dir, f"substring_{indx + 1}.txt"), "w", encoding="utf_8_sig") as file_stream:
            file_stream.write(sub_strings[indx])


# exit with msg and error code
def exit_error(usr_msg: str) -> None:
    print(f"ERROR: {usr_msg} \nERROR code {-1}")
    sys.exit(-1)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
