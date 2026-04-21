from typing import List, Dict


class ParsingError(Exception):
    pass


class ParsingFile:

    def __init__(self, count_nb_drones: int, count_nb_start_hub: int,
                 count_nb_end_hub: int, hub_data: dict,
                 connection_data: dict) -> None:
        self.count_nb_drones = count_nb_drones
        self.count_nb_start_hub = count_nb_start_hub
        self.count_nb_end_hub = count_nb_end_hub
        self.hub_data = hub_data
        self.connection_data = connection_data

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
            if len(values) > 4:
                raise ParsingError(f"too many values in {key}")
            elif len(values) < 3 or len(values) > 4:
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

        if ':' not in line:
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
                    raise ParsingError(
                        "The value of nb_drones most be a positive int and non '0'"
                    )
            except ValueError:
                raise ParsingError("The value of nb_drones most be an int")
            else:
                return nb

    def parse_hub(self, line: str, is_start: bool, is_end: bool, nb_drones: int) -> Dict:
        line = line.strip()

        if not line or line.startswith('#'):
            return

        if is_start and self.count_nb_start_hub != 1:
            raise ParsingError("Data most hold 1 start_hub")
        if is_end and self.count_nb_end_hub != 1:
            raise ParsingError("Data most hold 1 end_hub")

        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()
        val = val.split('#', 1)[0].strip().split(None, 3)

        if key == "start_hub":
            is_start = True
        if key == "end_hub":
            is_end = True

        if is_start and key != 'start_hub':
            raise ParsingError("Invalid 'start_hub' name")
        if is_end and key != 'end_hub':
            raise ParsingError("Invalid 'end_hub' name")
        if not is_start and not is_end and key != 'hub':
            raise ParsingError("Invalid 'hub' name")

        try:
            x = int(val[1])
            y = int(val[2])
        except ValueError:
            raise ParsingError("The value 'x, y' in hub most be an int")

        if 'hub' not in self.hub_data:
            self.hub_data['hub'] = {}
        
        if val[0][0] == '-':
            raise ParsingError(f"Name '{val[0]}' begin with '-'")
        
        if is_start:
            self.hub_data['hub']['start'] = {
                'name': val[0], 'X': x, 'Y': y,
                'properties': {'color': None, 'zone': 'normal', 'max_drones': 1}
            }
        elif is_end:
            self.hub_data['hub']['end'] = {
                'name': val[0], 'X': x, 'Y': y,
                'properties': {'color': None, 'zone': 'normal', 'max_drones': 1}
            }
        else:
            self.hub_data['hub'][val[0]] = {
                'name': val[0], 'X': x, 'Y': y,
                'properties': {'color': None, 'zone': 'normal', 'max_drones': 1}
            }

        if len(val) == 4:
            properties = val[3]
            if is_start:
                self.parse_properties(properties, 'start', nb_drones)
            elif is_end:
                self.parse_properties(properties, 'end', nb_drones)
            else:
                self.parse_properties(properties, val[0], nb_drones)

        return self.hub_data

    def parse_properties(self, properties_string: str, hub_type: str, nb_drones: int) -> None:
        try:
            properties_string = properties_string.split('[', 1)[1].strip()
            properties_string = properties_string.split(']', 1)[0].strip()
            properties_string = properties_string.split(None, 2)
        except Exception:
            raise ParsingError(f"The properties {properties_string} must be inside brackets []")
        
        if len(properties_string) != len(set(properties_string)):
            raise ParsingError("Duplicate properties")
        
        for val in properties_string:
            if '=' not in val:
                raise ParsingError(f"Invalid property format: '{val}', expected key=value")
            val = val.split('=', 1)
            if not val[0]:
                raise ParsingError("Property key cannot be empty")
            if not val[1]:
                raise ParsingError(f"Property '{val[0]}' has no value")
            if val[0] not in ['color', 'zone', 'max_drones']:
                raise ParsingError(f"Unknown property: '{val[0]}'")
            else:
                if val[0] == 'color':
                    if val[1] not in ['green', 'red', 'purple',
                                      'black', 'brown', 'orange', 'maroon',
                                      'gold', 'darkred', 'violet', 'crimson', 'rainbow']:
                        raise ParsingError(f"Unknown color: '{val[1]}'")
                    self.hub_data['hub'][hub_type]['properties']['color'] = val[1]
                elif val[0] == 'zone':
                    if val[1] not in ['restricted', 'priority']:
                        raise ParsingError(f"Unknown zone: '{val[1]}'")
                    self.hub_data['hub'][hub_type]['properties']['zone'] = val[1]
                elif val[0] == 'max_drones':
                    try:
                        num = int(val[1])
                        if num <= 0:
                            raise ParsingError(f"The value '{val[1]}' of '{val[0]}' must be > 0")
                        elif num > nb_drones:
                            raise ParsingError(f"The value '{val[1]}' of '{val[0]}' must be <= nb_drones")
                    except ValueError:
                        raise ParsingError(f"The value '{val[1]}' of '{val[0]}' must be an int")
                    self.hub_data['hub'][hub_type]['properties']['max_drones'] = int(val[1])

            

    # def parse_connection(line: str) -> None:
    #     line = line.strip()

    #     if not line or line.startswith('#'):
    #         return
        
    #     key, val = line.split(':', 1)
    #     key = key.strip()
    #     val = val.strip()
    #     val = val.split('#', 1)[0].strip().split(None, 2)




if __name__ == "__main__":
    parse = ParsingFile(
        count_nb_drones=0,
        count_nb_start_hub=0,
        count_nb_end_hub=0,
        hub_data={},
        connection_data={}
    )

    with open("maps/challenger/01_the_impossible_dream.txt") as f:
        try:
            for line in f:
                parse.parse_line(line)

            f.seek(0)
            dic = {}
            nb_drones = 0
            for line in f:
                result = parse.parse_drone__count(line)
                if result is not None:
                    nb_drones = result
                if 'start_hub' in line:
                    dic.update(parse.parse_hub(line, is_start=True, is_end=False, nb_drones=nb_drones))
                elif 'end_hub' in line:
                    dic.update(parse.parse_hub(line, is_start=False, is_end=True, nb_drones=nb_drones))
                elif 'hub' in line:
                    dic.update(parse.parse_hub(line, is_start=False, is_end=False, nb_drones=nb_drones))
                # elif 'connection' in line:
                #     dic.update(parse.parse_connection(line))

            print(dic)
        except Exception as e:
            print(f"Error: {e}")