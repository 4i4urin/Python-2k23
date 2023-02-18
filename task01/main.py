import sys

MAX_ARGC_NUM: int = len(["-f", "file.txt", "-d", "file1.txt", "-n", "100", "-l", "-r", "some"]) + 1
MIN_ARGC_NUM: int = len(["-f", "file.txt"]) + 1


# todo
# 2. checks flags in input --------
#     a. check min and max len ----
#     b. check unexpected flags ---
# 3. parse lines
# 4. Define Errors codes


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
    if flag_pos == 0:  # no -f
        return None
    elif flag_pos == len(argc) - 1:  # -f is last argument no file_name.txt
        return exit_error(100, "invalid command line flags")
    else:
        return argc[flag_pos + 1]


# find optional -flags in argc
def optional_argc(argc: list[str]) -> dict:
    flags: dict = {"n": find_postfix_flag("-n", argc), "d": check_txt_str(str(find_postfix_flag("-d", argc))),
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


def parse_line(in_str: str, str_len: int):
    pass


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


def main(argc: list[str]) -> int:
    f_name: str = required_argc(argc)
    flags: dir = optional_argc(argc)
    if f_name == flags["d"]:
        exit_error(100, "-f -d cannot be the same file")
    print(f_name)
    print(flags)
    with open(f_name, "r", encoding="utf_8_sig") as file_stream:
        f_str = file_stream.read()

    # parse_line(f_str, arg_flags["-n"])
    # print(f_str)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
