import sys
import os

MAX_ARGC_NUM: int = len(["-f", "file.txt", "-d", "dir", "-n", "100", "-l", "-r", "some"]) + 1
MIN_ARGC_NUM: int = len(["-f", "file.txt"]) + 1
DEFAULT_SUBSTRING_SIZE: int = 200


# todo
# 4. Define Errors codes


def main(argc: list[str]) -> int:
    f_name: str = required_argc(argc)
    flags: dict = optional_argc(argc)

    with open(f_name, "r", encoding="utf_8_sig") as file_stream:
        f_str = file_stream.read()

    if len(f_str) < flags["n"]:
        print(f"WARNING: -n {flags['n']} longer then string size {len(f_str)}")
        print(f"Will parse by default size {DEFAULT_SUBSTRING_SIZE}")
        flags["n"] = DEFAULT_SUBSTRING_SIZE

    undiv_strings: dict = create_undiv_str_dict(f_str, flags)

    parsed_strings: list[str] = parse_string(f_str, flags["n"], undiv_strings)
    # for checking parser work
    # len_sum: int = 0
    # for it in range(len(parsed_strings)):
    #     len_sum += len(parsed_strings[it])
    # print(f"len_parse = {len_sum}, len str = {len(f_str)}")
    # print(parsed_strings)
    print_substrings(parsed_strings, flags["d"])
    return 0


# check -f file_name.txt in argc
def required_argc(argc: list[str]) -> str:
    if len(argc) < MIN_ARGC_NUM:
        exit_error(101, "not enough command line arguments")
    if len(argc) > MAX_ARGC_NUM:
        exit_error(102, "too much command line arguments")
    file_name: str = check_txt_str(str(find_msg_after_flag("-f", argc)))
    if file_name is None:
        exit_error(103, "Expect -f file_name.txt in command line")
    return file_name


def check_txt_str(file_name: str) -> str | None:
    if file_name == str(None):
        return None
    if ".txt" in file_name:
        return file_name
    else:
        exit_error(201, "invalid file type require .txt file")


# return msg after -flag
def find_msg_after_flag(flag: str, argc: list[str]) -> str | None:
    flag_pos: int = 0
    # python should do this by itself, but I don't know how
    for index, it in enumerate(argc):
        if argc[index] == flag:
            flag_pos = index
            break
    if flag_pos == 0:  # no flag in argc
        return None
    elif flag_pos == len(argc) - 1:  # flag is last argument no msg after flag
        return exit_error(104, "invalid command line flags")
    else:
        return argc[flag_pos + 1]


# find optional -flags in argc
def optional_argc(argc: list[str]) -> dict:
    flags: dict = {"n": find_msg_after_flag("-n", argc), "d": find_msg_after_flag("-d", argc),
                   "r": find_msg_after_flag("-r", argc), "l": False if argc.count("-l") == 0 else True}
    if is_unexpected_flags(len(argc), flags):
        print("WARNING: unknown flags was ignored\nExpect: -f, -r, -n, -d, -l")
    # default value if no -n
    flags["n"]: str = str(DEFAULT_SUBSTRING_SIZE) if flags["n"] is None else flags["n"]
    if not flags["n"].isnumeric():
        exit_error(104, "Not number after -n")
    flags["n"]: int = int(flags["n"])  # hack, fix me
    return flags


# cmp expected and received flags return false if vals not eq
def is_unexpected_flags(argc_list_len: int, read_flags: dict) -> bool:
    receive_argc = MIN_ARGC_NUM
    for it in read_flags:
        if it == "l":  # flag without post msg
            receive_argc += 1 if True is read_flags[it] else 0
            continue
        if read_flags[it] is not None:
            receive_argc += 2
    if receive_argc != argc_list_len:
        return True
    return False


# return dictionary of undivided parts of string "@Kek Chel" [indx(@)] = indx(l)
def create_undiv_str_dict(string: str, flags: dict) -> dict:
    undiv_str_indx: dict = {}
    # start (st) finish (fin)
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
    at_indx: int = string.find("@")  # at = @
    score_indx: int = string.find("- Новый score пользователя @") if flags["l"] else len(string)
    if at_indx < score_indx:  # find @ first
        start_indx: int = at_indx
        finish_indx: int = string.find(":", start_indx, len(string))
    else:  # find Новый Score first
        start_indx: int = score_indx
        finish_indx: int = string.find("\n", start_indx, len(string))
    return start_indx, finish_indx


# return left border of undivided line if position_in_str in undivided line
def get_undiv_str_border(undiv_strings: dict, position_in_str: int) -> int:
    for it in undiv_strings.keys():
        if undiv_strings[it] > position_in_str > it:
            return it
    return position_in_str


def get_left_space(string: str, indx: int) -> int:
    if indx == len(string):
        return indx
    elif string[indx].isspace():
        return indx
    else:
        return max(string.rfind(" "), string.rfind("\n"), string.rfind("\t"),
                   string.rfind("\f"), string.rfind("\r"), string.rfind("\v"))


def get_right_border(string: str, undiv_strings: dict, prev_border: int, subline_size: int) -> int:
    right_border: int = get_undiv_str_border(undiv_strings, prev_border)
    new_border: int = get_left_space(string[0:right_border + 1], right_border)
    # + 1 to save space symbols in previous line
    return new_border + 1 if new_border != subline_size else new_border  # cannot put space in prev line


# kind of magic
def parse_string(string: str, subline_size: int, undiv_strings: dict) -> list[str]:
    right_border = get_right_border(string, undiv_strings, subline_size, subline_size)
    parsed_strings: list[str] = [string[0:right_border]]

    while right_border < len(string) - 1:
        left_border: int = right_border
        if len(string) < (right_border := right_border + subline_size):
            right_border = len(string)

        right_border = get_right_border(string, undiv_strings, right_border, subline_size)

        if right_border == left_border:
            if string[right_border:len(string)].isspace() or len(string) - right_border > subline_size:  # hack
                exit_error(301, f"Cannot parce line. Undivided parts longer then -n {subline_size}")
            else:  # no space in the end of file
                right_border = len(string)

        parsed_strings.append(string[left_border:right_border])

    return parsed_strings


# Just print substrings to command line and files is required
def print_substrings(sub_strings: list[str], new_directory: str) -> None:
    for it in range(len(sub_strings)):  # to command line
        print(f"\nSubstring #{it + 1} len = {len(sub_strings[it])}\n{sub_strings[it]}")
    if new_directory is None:  # if require
        return

    curent_directory: str = os.getcwd()  # to files
    new_directory: str = curent_directory + "\\" + new_directory
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)

    os.chdir(new_directory)
    for i in range(len(sub_strings)):
        with open(f"substring_{i + 1}.txt", "w", encoding="utf_8_sig") as file_stream:
            file_stream.write(sub_strings[i])
    os.chdir(curent_directory)


# exit with msg and error code
def exit_error(error_code: int, usr_msg: str) -> None:
    print(f"ERROR: {usr_msg} \nERROR code {error_code}")
    sys.exit(error_code)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
