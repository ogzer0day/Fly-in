from parsing import ParsingFile
from map import Map
from algorithm import Algos, Simulation
from visualisation import Visualizer
from typing import Any, Dict
import sys


if __name__ == "__main__":
    if (len(sys.argv) < 2) or (len(sys.argv) > 2):
        print("Error: the length of argument most be 2")
        exit(1)

    parse = ParsingFile(
        count_nb_drones=0,
        count_nb_start_hub=0,
        count_nb_end_hub=0,
        global_dict={'hub': {}, 'connections': []}
    )

    with open(sys.argv[1]) as f:
        try:
            count = 1
            for line in f:
                parse.parse_line(line, count)

            f.seek(0)
            dic: Dict[str, Any] = {}
            nb_drones = 0
            for line in f:
                result = parse.parse_drone__count(line, count)
                if result is not None:
                    nb_drones = result
                    dic.update({'nb_drones': nb_drones})
                if 'start_hub' in line:
                    hub_data = parse.parse_hub(
                        line, count, is_start=True, is_end=False,
                        nb_drones=nb_drones
                    )
                    if hub_data is not None:
                        dic.update(hub_data)
                elif 'end_hub' in line:
                    hub_data = parse.parse_hub(
                        line, count, is_start=False, is_end=True,
                        nb_drones=nb_drones
                    )
                    if hub_data is not None:
                        dic.update(hub_data)
                elif 'hub' in line:
                    hub_data = parse.parse_hub(
                        line, count, is_start=False, is_end=False,
                        nb_drones=nb_drones
                    )
                    if hub_data is not None:
                        dic.update(hub_data)
                elif 'connection' in line:
                    parse.parse_connection(line, count)

                count += 1
            parse.validate_connection_data(dic, count)

            map_obj = Map(dic)

            algo = Algos(map_obj)
            algo.k_shortest_path()

            drone_list = algo.allocate_dornes_to_list()
            sim = Simulation(drone_list, algo.paths, map_obj.all_hubs)

            viz = Visualizer(map_obj, sim)
            viz.run()
            sim.simulation()

        except Exception as e:
            print(f"Error: {e}")
