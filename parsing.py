from typing import List, Dict


class ParsingError(BaseException):
    pass


class ParsingFile:

    def parse(self, line: List) -> None:
        for chr in line:
            if chr == '#':
                raise ParsingError("Finding '#' in invalid place")

        if line[0] == "nb_drones":



        elif line[0] == "hub":

        elif line[0] == "connection":



if __name__ == "__main__":
    parsing = ParsingFile()

    try:
        with open("maps/challenger/01_the_impossible_dream.txt", 'r') as f:
            for line in f:
                striped: str = line.strip()
                if striped and striped[0] != '#':
                    key, val = line.split(':', 1)
                    data = [key.strip(), val.strip()]
                    print(data)
    except ParsingError as e:
        print("Error: e")