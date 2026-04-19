from typing import List, Dict


class ParsingError(Exception):
    pass


class ParsingFile:
    
    def __init__(self, count_nb_drones: int, count_nb_start_hub: int,
                count_nb_end_hub: int) -> None:
        self.count_nb_drones = count_nb_drones
        self.count_nb_start_hub = count_nb_start_hub
        self.count_nb_end_hub = count_nb_end_hub

    def parse_line(self, line: str) -> None:

        line = line.strip()

        if not line or line.startswith('#'):
            return

        if ':' not in line:
            raise ParsingError("Invalid data, data should hold ':'")

        key, val = line.split(':', 1)
        key = key.strip()
        
        if key in ['hub', 'start_hub', 'end_hub']:
            values = val.split('#', 1)[0].strip().split(None, 3)
            if len(values) < 3 or len(values) > 4:
                raise ParsingError(f"Invalid {key}")
            elif key == 'start_hub':
                self.count_nb_start_hub += 1
            elif key == 'end_hub':
                self.count_nb_end_hub += 1

            if len(values) >= 3:
                if not values[1].strip('-').isdigit() or not values[2].strip('-').isdigit():
                    raise ParsingError("Invalid data, should be hold a digit number")
                
        elif key == 'nb_drones':
            values = val.split('#', 1)[0].strip().split()
            if len(values) != 1:
                raise ParsingError("Invalid nb_drones data")
            self.count_nb_drones += 1
            
        elif key == 'connection':
            values = val.split('#', 1)[0].strip().split(None, 2)
            if len(values) < 1 or len(values) > 2:
                raise ParsingError("Invalid connection data")
            
        if self.count_nb_drones > 1:
            raise ParsingError("too many nb_drones")
        if self.count_nb_end_hub > 1:
            raise ParsingError("too many nb_end_hub")
        if self.count_nb_start_hub > 1:
            raise ParsingError("too many nb_start_hub")



if __name__ == "__main__":
    parse = ParsingFile(count_nb_drones=0, count_nb_start_hub=0,
                        count_nb_end_hub=0)

    with open("maps/challenger/01_the_impossible_dream.txt") as f:
        try:
            for line in f:
                parse.parse_line(line)
        except Exception as e:
            print(f"Error: {e}")