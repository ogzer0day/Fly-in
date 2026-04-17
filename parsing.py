from typing import List, Dict


class ParsingError(Exception):
    pass


class ParsingFile:

    def parse_line(self, line: str) -> None:
        line = line.strip()

        if not line or line.startswith('#'):
            return

        if ':' not in line:
            raise ParsingError("Invalid data, data should hold ':'")

        key, val = line.split(':', 1)
        key = key.strip()
        
        if key.strip('#') in "nb_drones" and key.startswith('#'):
            raise ParsingError("Invalid data")
        
        if key in ['hub', 'start_hub', 'end_hub']:
            values = val.split('#', 1)[0].strip().split(None, 3)
            if len(values) < 3 or len(values) > 4:
                raise ParsingError("Invalid data")

            if len(values) >= 3:
                if not values[1].strip('-').isdigit() or not values[2].strip('-').isdigit():
                    raise ParsingError("Invalid data")
                
        elif key == 'nb_drones':
            values = val.split('#', 1)[0].strip().split()
            if len(values) != 1:
                raise ParsingError("Invalid data")
            
        elif key == 'connection':
            values = val.split('#', 1)[0].strip().split(None, 2)
            if len(values) < 1 or len(values) > 2:
                raise ParsingError("Invalid data")

if __name__ == "__main__":
    parse = ParsingFile()

    with open("maps/challenger/01_the_impossible_dream.txt") as f:
        try:
            for line in f:
                parse.parse_line(line)
        except Exception as e:
            print(f"Error: {e}")