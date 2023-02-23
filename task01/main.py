import sys
import os

MAX_ARGC_NUM: int = len(["-f", "file.txt", "-d", "file1.txt", "-n", "100", "-l", "-r", "some"]) + 1
MIN_ARGC_NUM: int = len(["-f", "file.txt"]) + 1


# todo
# 4. Define Errors codes
# 5. refactor code


# check -f file_name.txt in argc
def required_argc(argc: list[str]) -> str:
    if len(argc) < MIN_ARGC_NUM:
        exit_error(100, "not enough command line arguments")
    if len(argc) > MAX_ARGC_NUM:
        exit_error(100, "too much command line arguments")
    file_name: str = check_txt_str(str(find_postfix_flag("-f", argc)))
    if file_name is None:
        exit_error(100, "Expect -f file_name.txt in command line")
    return file_name


def check_txt_str(file_name: str) -> str | None:
    if file_name == str(None):
        return None
    if ".txt" in file_name:
        return file_name
    else:
        exit_error(100, "invalid file type require .txt file")


# return msg after -flag
def find_postfix_flag(flag: str, argc: list[str]) -> str | None:
    flag_pos: int = 0
    # python should do this by itself, but I don't know how
    for index, it in enumerate(argc):
        if argc[index] == flag:
            flag_pos = index
            break
    if flag_pos == 0:  # no flag in argc
        return None
    elif flag_pos == len(argc) - 1:  # flag is last argument no msg after flag
        return exit_error(100, "invalid command line flags")
    else:
        return argc[flag_pos + 1]


# find optional -flags in argc
def optional_argc(argc: list[str]) -> dict:
    flags: dict = {"n": find_postfix_flag("-n", argc), "d": find_postfix_flag("-d", argc),
                   "r": find_postfix_flag("-r", argc), "l": False if argc.count("-l") == 0 else True}
    if is_unexpected_flags(len(argc), flags):
        print("WARNING: unknown flags was ignored\nExpect: -f, -r, -n, -d, -l")
    # default value if no -n
    flags["n"]: str = "200" if flags["n"] is None else flags["n"]
    if not flags["n"].isnumeric():
        exit_error(100, "Not number after -n")
    flags["n"]: int = int(flags["n"])  # hack, fix me
    return flags


# exit with msg and error code
def exit_error(error_code: int, usr_msg: str) -> None:
    print(f"ERROR: {usr_msg} \nERROR code {error_code}")
    sys.exit(error_code)


# @ to :, if -l Новый Score to \n
def find_undivided_part(string: str, flags: dir) -> tuple[int, int]:
    # print(string)
    at_indx: int = string.find("@")  # at = @
    score_indx: int = string.find("- Новый score пользователя @") if flags["l"] else len(string)
    if at_indx < score_indx:  # find @ first
        start_indx: int = at_indx
        finish_indx: int = string.find(":", start_indx, len(string))
    else:  # find Новый Score first
        start_indx: int = score_indx
        finish_indx: int = string.find("\n", start_indx, len(string))
    return start_indx, finish_indx


# cmp expected and received flags return false if vals not eq
def is_unexpected_flags(count_list_len: int, read_flags: dict) -> bool:
    count_receive_argc = MIN_ARGC_NUM
    for it in read_flags:
        if it == "l":  # flag without postfix msg
            count_receive_argc += 1 if True is read_flags[it] else 0
            continue
        if read_flags[it] is not None:
            count_receive_argc += 2
    if count_receive_argc != count_list_len:
        return True
    return False


def create_undiv_str_dict(string: str, flags: dict) -> dict:
    undiv_str_idx: dict = {}
    # start (st) finish (fin)
    string_shift: int = 0
    while True:
        st_i, fin_i = find_undivided_part(string[string_shift:len(string)], flags)
        if st_i == -1 or fin_i == -1:
            break
        undiv_str_idx[st_i + string_shift] = fin_i + string_shift
        string_shift += fin_i
    return undiv_str_idx


# rename
def get_undiv_str_border(undiv_strings: dict, position_in_str: int) -> int:
    for it in undiv_strings.keys():
        if undiv_strings[it] > position_in_str > it:
            return it
    return position_in_str


def get_left_space(string: str, indx: int) -> int:
    if string[indx - 1].isspace():
        return indx - 1
    else:
        return max(string.rfind(" "), string.rfind("\n"), string.rfind("\t"),
                   string.rfind("\f"), string.rfind("\r"), string.rfind("\v"))


# rename all values
def parse_string(string: str, subline_size: int, undiv_strings: dict) -> list[str]:
    string_shift: int = 0

    position_string: int = get_undiv_str_border(undiv_strings, subline_size)
    parsed_strings: list[str] = [string[string_shift:position_string]]

    while position_string < len(string) - 1:

        string_shift = position_string
        if len(string) < (position_string := position_string + subline_size):
            position_string = len(string)

        position_string = get_undiv_str_border(undiv_strings, position_string)
        position_string = get_left_space(string[0:position_string + 1], position_string)

        if position_string == string_shift:
            exit_error(200, f"Cannot parce line. Undivided string longer then -n {subline_size}")

        parsed_strings.append(string[string_shift:position_string])
    return parsed_strings


def print_substrings(sub_strings: list[str], new_directory: str) -> None:
    for it in range(len(sub_strings)):
        print(f"\nSubstring #{it + 1} len = {len(sub_strings[it])}\n{sub_strings[it]}")
    if new_directory is None:
        return

    curent_directory: str = os.getcwd()
    new_directory: str = curent_directory + "\\" + new_directory
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)

    os.chdir(new_directory)
    for i in range(len(sub_strings)):
        with open(f"substring_{i + 1}.txt", "w", encoding="utf_8_sig") as file_stream:
            file_stream.write(sub_strings[i])
    os.chdir(curent_directory)


def main(argc: list[str]) -> int:
    f_name: str = required_argc(argc)
    flags: dict = optional_argc(argc)
    if f_name == flags["d"]:
        exit_error(100, "-f -d cannot be the same file")
    # print(f_name)
    print(flags)
    with open(f_name, "r", encoding="utf_8_sig") as file_stream:
        f_str = file_stream.read()

    if len(f_str) < flags["n"]:
        print(f"WARNING: -n {flags['n']} longer then string size {len(f_str)}")

    undiv_strings: dict = create_undiv_str_dict(f_str, flags)

    parsed_strings: list[str] = parse_string(f_str, flags["n"], undiv_strings)
    print_substrings(parsed_strings, flags["d"])
    # output_strings(parsed_strings, flags["d"])
    # print(f_str)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
