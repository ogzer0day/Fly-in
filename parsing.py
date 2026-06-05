from typing import Dict, Any, Optional


class ParsingError(Exception):
    """Custom exception for parsing errors."""

    pass


class ParsingFile:
    """Parser for network configuration files."""

    def __init__(
        self,
        count_nb_drones: int,
        count_nb_start_hub: int,
        count_nb_end_hub: int,
        global_dict: Dict[str, Any],
    ) -> None:
        """Initialize parser with counters and data dictionary."""
        self.count_nb_drones = count_nb_drones
        self.count_nb_start_hub = count_nb_start_hub
        self.count_nb_end_hub = count_nb_end_hub
        self.global_dict = global_dict

    def parse_line(self, line: str, count: int) -> None:
        """Parse and validate a single line from configuration file."""
        line = line.strip()

        if not line or line.startswith('#'):
            return

        if ':' not in line:
            raise ParsingError(
                f"In line {count}, invalid data, data should hold ':'"
            )

        key, val = line.split(':', 1)
        key = key.strip()

        if key in ['hub', 'start_hub', 'end_hub']:
            values = val.split('#', 1)[0].strip().split(None, 3)
            if len(values) > 4:
                raise ParsingError(
                    f"In line {count}, too many values in {key}"
                )
            elif len(values) < 3 or len(values) > 4:
                raise ParsingError(f"In line {count}, invalid {key}")
            elif key == 'start_hub':
                self.count_nb_start_hub += 1
            elif key == 'end_hub':
                self.count_nb_end_hub += 1

            if len(values) >= 3:
                if (not values[1].strip('-').isdigit() or
                        not values[2].strip('-').isdigit()):
                    raise ParsingError(
                        f"In line {count}, invalid data, should be "
                        f"hold a digit number"
                    )

        elif key == 'nb_drones':
            values = val.split('#', 1)[0].strip().split()
            if len(values) != 1:
                raise ParsingError(
                    f"In line {count}, invalid nb_drones data"
                )
            self.count_nb_drones += 1

        elif key == 'connection':
            values = val.split('#', 1)[0].strip().split(None, 2)
            if len(values) < 1 or len(values) > 2:
                raise ParsingError(
                    f"In line {count}, invalid connection data"
                )

    def parse_drone__count(
        self, line: str, count: int
    ) -> Optional[int]:
        """Parse drone count from line and return number."""
        line = line.strip()

        if not line or line.startswith('#'):
            return None

        if ':' not in line:
            return None

        if self.count_nb_drones != 1:
            raise ParsingError(
                f"In line {count}, data most hold 1 nb_drones"
            )

        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()

        if key == 'nb_drones':
            try:
                nb = int(val)
                if nb <= 0:
                    raise ParsingError(
                        f"In line {count}, value of nb_drones most be "
                        f"a positive int and non '0'"
                    )
            except ValueError:
                raise ParsingError(
                    f"In line {count}, value of nb_drones most be an int"
                )
            else:
                return nb
        return None

    def parse_hub(
        self,
        line: str,
        count: int,
        is_start: bool,
        is_end: bool,
        nb_drones: int,
    ) -> Optional[Dict[str, Any]]:
        """Parse hub definition from line."""
        line = line.strip()

        if not line or line.startswith('#'):
            return None

        if is_start and self.count_nb_start_hub != 1:
            raise ParsingError(
                f"In line {count}, data most hold 1 start_hub"
            )
        if is_end and self.count_nb_end_hub != 1:
            raise ParsingError(
                f"In line {count}, data most hold 1 end_hub"
            )

        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()
        val_list = val.split('#', 1)[0].strip().split(None, 3)

        if key == "start_hub":
            is_start = True
        if key == "end_hub":
            is_end = True

        if is_start and key != 'start_hub':
            raise ParsingError(
                f"In line {count}, invalid 'start_hub' name"
            )
        if is_end and key != 'end_hub':
            raise ParsingError(
                f"In line {count}, invalid 'end_hub' name"
            )
        if not is_start and not is_end and key != 'hub':
            raise ParsingError(f"In line {count}, invalid {key} name")

        try:
            x = int(val_list[1])
            y = int(val_list[2])
        except ValueError:
            raise ParsingError(
                f"In line {count}, value 'x, y' in hub most be an int"
            )

        if 'hub' not in self.global_dict:
            self.global_dict['hub'] = {}

        if val_list[0][0] == '-':
            raise ParsingError(
                f"In line {count}, name '{val_list[0]}' begin with '-'"
            )

        if is_start:
            self.global_dict['hub']['start'] = {
                'name': val_list[0], 'X': x, 'Y': y,
                'properties': {
                    'color': None, 'zone': 'normal', 'max_drones': 1
                }
            }
        elif is_end:
            self.global_dict['hub']['end'] = {
                'name': val_list[0], 'X': x, 'Y': y,
                'properties': {
                    'color': None, 'zone': 'normal', 'max_drones': 1
                }
            }
        else:
            self.global_dict['hub'][val_list[0]] = {
                'name': val_list[0], 'X': x, 'Y': y,
                'properties': {
                    'color': None, 'zone': 'normal', 'max_drones': 1
                }
            }

        if len(val_list) == 4:
            properties = val_list[3]
            if is_start:
                self.parse_properties(
                    properties, 'start', nb_drones, count
                )
            elif is_end:
                self.parse_properties(
                    properties, 'end', nb_drones, count
                )
            else:
                self.parse_properties(
                    properties, val_list[0], nb_drones, count
                )

        return self.global_dict

    def parse_properties(
        self,
        properties_string: str,
        hub_type: str,
        nb_drones: int,
        count: int,
    ) -> None:
        """Parse hub properties (color, zone, max_drones)."""
        try:
            props_str = properties_string.split('[', 1)[1].strip()
            props_str = props_str.split(']', 1)[0].strip()
            properties_list: list[str] = props_str.split(None, 2)
        except Exception:
            raise ParsingError(
                f"In line {count}, properties {properties_string} "
                f"must be inside brackets []"
            )

        if len(properties_list) != len(set(properties_list)):
            raise ParsingError(
                f"In line {count}, duplicate properties"
            )

        for val in properties_list:
            if '=' not in val:
                raise ParsingError(
                    f"In line {count}, invalid property format: '{val}', "
                    f"expected key=value"
                )
            prop_parts = val.split('=', 1)
            if not prop_parts[0]:
                raise ParsingError(
                    f"In line {count}, property key cannot be empty"
                )
            if not prop_parts[1]:
                raise ParsingError(
                    f"In line {count}, property '{prop_parts[0]}' "
                    f"has no value"
                )
            if prop_parts[0] not in ['color', 'zone', 'max_drones']:
                raise ParsingError(
                    f"In line {count}, unknown property: "
                    f"'{prop_parts[0]}'"
                )
            else:
                if prop_parts[0] == 'color':
                    valid_colors = [
                        'green', 'red', 'purple', 'black', 'brown',
                        'orange', 'maroon', 'gold', 'darkred',
                        'violet', 'crimson', 'rainbow', 'blue',
                        'yellow', 'cyan', 'lime', 'magenta'
                    ]
                    if prop_parts[1] not in valid_colors:
                        raise ParsingError(
                            f"In line {count}, unknown color: "
                            f"'{prop_parts[1]}'"
                        )
                    self.global_dict['hub'][hub_type]['properties'][
                        'color'
                    ] = prop_parts[1]
                elif prop_parts[0] == 'zone':
                    zone = [
                        'normal', 'blocked', 'restricted', 'priority'
                    ]
                    if prop_parts[1] not in zone:
                        raise ParsingError(
                            f"In line {count}, unknown zone: "
                            f"'{prop_parts[1]}'"
                        )
                    self.global_dict['hub'][hub_type]['properties'][
                        'zone'
                    ] = prop_parts[1]
                elif prop_parts[0] == 'max_drones':
                    try:
                        num = int(prop_parts[1])
                        if num <= 0:
                            raise ParsingError(
                                f"In line {count}, value "
                                f"'{prop_parts[1]}' of "
                                f"'{prop_parts[0]}' must be > 0"
                            )
                    except ValueError:
                        raise ParsingError(
                            f"In line {count}, value "
                            f"'{prop_parts[1]}' of "
                            f"'{prop_parts[0]}' must be an int"
                        )
                    self.global_dict['hub'][hub_type]['properties'][
                        'max_drones'
                    ] = int(prop_parts[1])

    def parse_connection(self, line: str, count: int) -> None:
        """Parse network connection between two hubs."""
        line = line.strip()

        if not line or line.startswith('#'):
            return

        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()
        val_list = val.split('#', 1)[0].strip().split(None, 2)

        z_names = val_list[0].split('-', 1)
        if len(z_names) != 2:
            raise ParsingError(
                f"In line {count}, connection syntax have to be "
                f"'<name1>-<name2>'"
            )

        if len(z_names) != len(set(z_names)):
            raise ParsingError(
                f"In line {count}, duplicate name {z_names[0]} "
                f"in one line"
            )

        if len(val_list) == 2:
            try:
                metadata = val_list[1].split('[', 1)[1].strip()
                metadata = metadata.split(']', 1)[0].strip()
                meta_list = metadata.split('=', 1)
            except Exception:
                raise ParsingError(
                    f"In line {count}, properties must be inside "
                    f"brackets []"
                )

            if len(meta_list) != 2 or meta_list[0] != "max_link_capacity":
                raise ParsingError(
                    f"In line {count}, metadata syntax has to be "
                    f"'max_link_capacity=<number>'"
                )

            try:
                max_link_capacity_num = int(meta_list[1])
                if max_link_capacity_num <= 0:
                    raise ParsingError(
                        f"In line {count}, num of max_link_capacity "
                        f"has to be a positive int"
                    )
            except ValueError:
                raise ParsingError(
                    f"In line {count}, num of max_link_capacity "
                    f"has to be an int"
                )

            if 'connections' not in self.global_dict:
                self.global_dict['connections'] = []

            self.global_dict['connections'].append(
                ((z_names[0], z_names[1]), {
                    meta_list[0]: max_link_capacity_num
                })
            )
        elif len(val_list) == 1:
            self.global_dict['connections'].append(
                ((z_names[0], z_names[1]), {
                    'max_link_capacity': 1
                })
            )
        names = [
            hub['name'] for hub in self.global_dict['hub'].values()
        ]

        if z_names[0] not in names:
            raise ParsingError(
                f"In line {count}, hub name '{z_names[0]}' not found"
            )
        if z_names[1] not in names:
            raise ParsingError(
                f"In line {count}, hub name '{z_names[1]}' not found"
            )

    def validate_connection_data(
        self, data: Dict[str, Any], count: int
    ) -> None:
        """Validate connections for duplicates."""
        seen: set[tuple[str, str]] = set()

        for (a, b), _ in data['connections']:
            key = tuple(sorted((a, b)))

            if key in seen:
                raise ParsingError(
                    f"In line {count}, duplicate connection detected: "
                    f"{a}-{b}"
                )

            seen.add(key)
