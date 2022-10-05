from components import *
import time

def MCTS(requirements = None, run_time = 1, available_components = None):
    if requirements is None or available_components is None:
        return -1

    start = time.time()
    root = Node(requirements=requirements)
    root.set_as_root()

    good_nodes = []
    best_node = root
    iter = 0

    while( time.time() - start < run_time):
        promising_node = Selection(root)
        if promising_node.is_terminal(available_components, requirements):
            continue
        node_to_explore = promising_node.expand(available_components=available_components, requirements=requirements)
        node_to_explore.visit_count += 1
        best_node, good_nodes = Simulation(node_to_explore, best_node, good_nodes, requirements, available_components)
        iter += 1
    
    good_nodes.reverse()
    return Solution(nodes = good_nodes, iter = iter)

def Simulation(starting_Node, best_node, good_nodes, requirements, available_components):
    node = starting_Node
    while not node.is_terminal(available_components,requirements):
        node.add_random_child(available_components, requirements)
        node = node.get_random_child()
    
    if node.score > best_node.score:
        best_node = node
        good_nodes.append(node)
    
    while not node.root and node.parent is not None:
        node = node.parent
        node.calculate_score()
        if node.visit_count == 0:
            node.children.clear()

    return best_node, good_nodes

def Selection(root):
    node = root
    node.visit_count += 1
    while not node.leaf:
        node = node.get_best_child()
        node.visit_count += 1
    return node
        