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
            if len(values) > 5:
                raise ParsingError(f"too many values in {key}")
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

    def parse_drone__count(self, line: str) -> int:
        line = line.strip()

        if not line or line.startswith('#'):
            return

        if self.count_nb_drones != 1:
            raise ParsingError("Data most hold 1 nb_drones")
        
        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()

        if key == 'nb_drones':
            try:
                nb = int(val)
                if nb <= 0:
                    raise ParsingError ("The value of nb_drones most be a" \
                    "positive int and non '0'")
            except ValueError:
                raise ParsingError(f"The value of nb_drones most be an int")
            else:
                return (nb)

    

if __name__ == "__main__":
    parse = ParsingFile(count_nb_drones=0, count_nb_start_hub=0,
                        count_nb_end_hub=0)

    with open("maps/challenger/01_the_impossible_dream.txt") as f:
        try:
            for line in f:
                parse.parse_line(line)
            f.seek(0)
            for line in f:
                result = parse.parse_drone__count(line)
                if result is not None:
                    nb_drones = result
                # parse.parse_hub(line, is_start=False, is_end=False)
                # parse.parse_connection(line)
            print(nb_drones)
        except Exception as e:
            print(f"Error: {e}")