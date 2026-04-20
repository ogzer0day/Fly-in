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
            returncolor==red

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


    # def parse_properties(self, properties_string: str, hub_type: str) -> None:
    #     properties_string = properties_string.split('[', 1)[1].strip()
    #     properties_string = properties_string.split(']', 1)[0].strip()
    #     properties_string = properties_string.split(None, 2)
    #     properties_string = properties_string.split(' ', 1)[0]

    #     for val in properties_string:
    #         val = val.split('=', 1)
    #         if val[1][0] == '=':
    #             raise ParsingError("Invalid properties have more than one '='")
    #         else:
    #             if val[0] == 'color':
    #                 hub_data[hub_type]['properties']['color'] = val[1]
    #             elif val[0] == 'zone':
    #                 hub_data[hub_type]['properties']['zone'] = val[1]
    #             elif val[0] == 'max_drones':
    #                 hub_data[hub_type]['properties']['max_drones'] = val[1]


    def parse_hub(self, line: str, is_start: bool, is_end:bool) -> Dict:
        line = line.strip()

        if not line or line.startswith('#'):
            return
        
        if is_start and self.count_nb_start_hub != 1:
            raise ParsingError("Data most hold 1 start_hub")
        if is_end and self.count_nb_end_hub!= 1:
            raise ParsingError("Data most hold 1 end_hub")

        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()
        val = val.split('#', 1)[0].strip().split(None, 3)

        name = val[0]
        if is_start and name not in 'start_hub':
            raise ParsingError("Invalid 'start_hub' name")
        elif is_end and name not in 'end_hub':
            raise ParsingError("Invalid 'end_hub' name")
        elif not is_start and not is_end and name not in 'hub':
            raise ParsingError("Invalid 'hub' name")
        try:
            x = int(val[1])
            y = int(val[2])
        except ValueError:
            raise ParsingError("The value 'x, y' in hub most be an int")
        

        if is_start:
            self.hub_data['start'] = {'name': name, 'X': x, 'Y': y, 'properties': {'color': None, 'zone': 'normal', 'max_drones': 1}}
        elif is_end:
            self.hub_data['end'] = {'name': name, 'X': x, 'Y': y, 'properties': {'color': None, 'zone': 'normal', 'max_drones': 1}}
        else:
            self.hub_data['hub'] = {'name': name, 'X': x, 'Y': y, 'properties': {'color': None, 'zone': 'normal', 'max_drones': 1}}

        if len(val) == 4:
            properties = val[3]
            if is_start:
                parse_properties(properties, 'start')
            elif is_end:
                parse_properties(properties, 'end')
            else:
                parse_properties(properties, 'hub')

        print(self.hub_data)


if __name__ == "__main__":
    parse = ParsingFile(count_nb_drones=0, count_nb_start_hub=0,
                        count_nb_end_hub=0, hub_data={}, connection_data={})

    with open("maps/challenger/01_the_impossible_dream.txt") as f:
        try:
            for line in f:
                parse.parse_line(line)
            f.seek(0)
            for line in f:
                result = parse.parse_drone__count(line)
                if result is not None:
                    nb_drones = result
                if 'start_hub' in line:
                    parse.parse_hub(line, is_start=True, is_end=False)
                if 'end_hub' in line:
                    parse.parse_hub(line, is_start=False, is_end=True)
                if 'hub' in line:
                    parse.parse_hub(line, is_start=False, is_end=False)
                
                # parse.parse_connection(line)
            print(nb_drones)
        except Exception as e:
            print(f"Error: {e}")