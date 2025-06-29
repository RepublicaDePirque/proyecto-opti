import numpy as np
import random
import pulp
from pulp import LpProblem, LpVariable, LpMinimize, lpSum


g_diameters = [1, 3, 4]
g_costs_a = {1: 16, 3: 24, 4: 27}
g_costs_b = {1: 45, 3: 62, 4: 68}
g_capacities = {1: 353, 3: 1414, 4: 2036}

g_ranges = {
    'small': {
        'plants': (1, 2),
        'pipes': (5, 10),
        'transbord_client': (5, 10),
        'final_client': (10, 20),
    },
    'medium': {
        'plants': (3, 4),
        'pipes': (10, 20),
        'transbord_client': (10, 20),
        'final_client': (20, 50),
    },
    'large': {
        'plants': (5, 7),
        'pipes': (20, 50),
        'transbord_client': (25, 50),
        'final_client': (50, 100),
    }
}

def generate_nodes(type, count) -> list:
    return [f"{type}{i+1}" for i in range(count)]

def generate_edges(start, final) -> list:
    edges = {}
    for i in start:
        for j in final:
            if i not in edges:
                edges[i] = []
            edges[i].append(j)
    return edges

def generate_instance(tamano='small', seed=None) -> dict:
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    print(f"Used seed: {seed}")
    
    n_plants = random.randint(*g_ranges[tamano]['plants'])
    
    plants = generate_nodes('plant', n_plants)
    pipes = generate_nodes('pipe', random.randint(*g_ranges[tamano]['pipes']))
    transbord_client = generate_nodes('transbord_client', random.randint(*g_ranges[tamano]['transbord_client']))
    final_client = generate_nodes('final_client', random.randint(*g_ranges[tamano]['final_client']))
    
    edge_to_plant_pipes = generate_edges(plants, pipes)
    edge_pipes_to_transbord = generate_edges(pipes, transbord_client)
    edge_transbord_client_to_final_client = generate_edges(transbord_client, final_client)
    
    graph = {}
    graph.update(edge_to_plant_pipes)
    graph.update(edge_pipes_to_transbord)
    graph.update(edge_transbord_client_to_final_client)
    
    requests = {c: round(random.uniform(40, 100), 2) for c in final_client}
    
    prices = {}
    all_possible_edges_for_prices = []
    for start_node, end_nodes_list in graph.items():
        for end_node in end_nodes_list:
            all_possible_edges_for_prices.append((start_node, end_node))

    for (i, j) in all_possible_edges_for_prices:
        price_ij = np.random.normal(8, 2)
        if price_ij < 1:
            price_ij = 1.0
        prices[(i,j)] = round(price_ij, 2)
    
    total_price= sum(requests.values())
    supply_per_plant = round(total_price / n_plants, 2)
    supplys = {p: supply_per_plant for p in plants}
    
    instance = {
        'plants': plants,
        'pipes': pipes,
        'transbord_client': transbord_client,
        'final_client': final_client,
        'graph': graph,
        'requests': requests,
        'transport_prices': prices,
        'supplys': supplys,
        'diameters': g_diameters,
        'cost_a': g_costs_a,
        'cost_b': g_costs_b,
        'capacity': g_capacities
    }
    
    return instance

def print_instance(instance):
    print("Plants:", instance['plants'])
    print("Pipes:", instance['pipes'])
    print("Transbord clients:", instance['transbord_client'])
    print("Final clients:", instance['final_client'])
    print("\nGraph origin -> destination:")
    for origin_node, destination_nodes in instance['graph'].items():
        for dest_node in destination_nodes:
            print(f"  {origin_node} -> {dest_node}")
    print("\nRequests final clients:")
    for key, value in instance['requests'].items():
        print(f"  {key}: {value} l/min")
    print("\nTransport_prices (per edge):")
    for key, value in instance['transport_prices'].items():
        print(f"  {key[0]}->{key[1]}: {value}")
    print("\nPlants supplys:")
    for key, value in instance['supplys'].items():
        print(f"  {key}: {value} l/min")
    print("\nDiameters availavle:", instance['diameters'])
    print("Cost instalation type A:", instance['cost_a'])
    print("Cost instalation type B:", instance['cost_b'])
    print("Capacity per diameter:", instance['capacity'])


import io

def build_and_export_model(instance, filename):
    diameters = instance["diameters"]
    capacities = instance["capacity"]
    cost_a = instance["cost_a"]
    cost_b = instance["cost_b"]
    prices = instance["transport_prices"]
    graph_edges_tuples = []
    for i, j_list in instance['graph'].items():
        for j in j_list:
            graph_edges_tuples.append((i, j))


    with open(filename, 'w') as f:
        f.write("min: ") 

        objective_terms = []
        for (i, j) in graph_edges_tuples: 
            for d in diameters:
                objective_terms.append(f"{prices[(i, j)]} x_{i}_{j}_d{d}")
                objective_terms.append(f"{cost_a[d]} y_{i}_{j}_d{d}")
                objective_terms.append(f"{cost_b[d]} y_{i}_{j}_d{d}")
        f.write(" + ".join(objective_terms) + ";\n")

        for (i, j) in graph_edges_tuples:
            for d in diameters:
                f.write(f"  x_{i}_{j}_d{d} <= {capacities[d]} y_{i}_{j}_d{d};\n")

        for (i, j) in graph_edges_tuples:
            f.write(f"  " + " + ".join([f"y_{i}_{j}_d{d}" for d in diameters]) + " = 1;\n")

        all_nodes = set(instance["plants"] + instance["pipes"] + instance["transbord_client"] + instance["final_client"])
        
        node_inputs = {node: [] for node in all_nodes}
        node_outputs = {node: [] for node in all_nodes}

        for (i, j) in graph_edges_tuples:
            for d in diameters:
                node_outputs[i].append(f"x_{i}_{j}_d{d}")
                node_inputs[j].append(f"x_{i}_{j}_d{d}")

        for node in all_nodes:
            input_sum_str = " + ".join(node_inputs[node]) if node_inputs[node] else "0"
            output_sum_str = " + ".join(node_outputs[node]) if node_outputs[node] else "0"

            if node in instance["plants"]:
                f.write(f"  {output_sum_str} <= {instance['supplys'][node]};\n") 

            elif node in instance["final_client"]:
                f.write(f"  {input_sum_str} = {instance['requests'][node]};\n")

            else:
                f.write(f"  {input_sum_str} = {output_sum_str};\n")

    print(f"Modelo exportado a {filename}")
instance = generate_instance('large', seed=122)
build_and_export_model(instance,"transbordo.lp")
