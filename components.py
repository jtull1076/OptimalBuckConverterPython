from doctest import OutputChecker
from math import log, sqrt, exp
from operator import truediv
from pickletools import read_uint1
import random
from dataclasses import dataclass
import re
import string
from csv import reader
from typing import List


class Requirements:
    'Defines the requirements for the buck converter'

    def __init__(self, min_input_voltage = 0, max_input_voltage = 0, 
    output_voltage = 0, output_current = 0, performance_weight = 0, cost_weight = 0) -> None:
        self.min_input_voltage = min_input_voltage
        self.max_input_voltage = max_input_voltage
        self.output_voltage = output_voltage
        self.output_current = output_current
        self.performance_weight = performance_weight
        self.cost_weight = cost_weight


class Node:
    'Defines a Node on the tree (a combination of components)'

    def __init__(self, state = None, parent = None, requirements = None) -> None:
        
        if state:
            self.components = state
        else:
            self.components = State()

        if self.components.is_complete_state():
            self.score = self.calculate_score(requirements)
        else:
            self.score = 0

        self.parent = parent
        self.children = []
        self.root = False
        self.leaf = True
        self.visit_count = 0


    def set_as_root(self):
        self.root = True

    def is_fully_expanded(self, available_components, requirements):
        available_new_components = self.components.get_all_possible_states(available_components, requirements)
        if (len(available_new_components) == len(self.children)):
            return True
        else:
            return False

    def expand(self, available_components = None, requirements = None):
        available_new_components = self.components.get_all_possible_states(available_components = available_components, requirements = requirements)
        node_to_explore = self
        for components in available_new_components:
            child_already_created = False
            for child in self.children:
                if (child.components.chip == components.chip and child.components.inductor==components.inductor and child.components.out_cap == components.out_cap and child.components.in_cap == components.in_cap):
                        child_already_created = True
                        break
            if not child_already_created:
                node_to_explore = Node(components, self)
                self.children.append(node_to_explore)
                break
        
        if (self.is_fully_expanded(available_components, requirements)):
            leaf = False

        return node_to_explore

    
    def add_random_child(self, available_components = None, requirements = None):
        available_new_components = self.components.get_all_possible_states(available_components=available_components, requirements = requirements)
        if available_components is not None:
            self.children.append(Node(state = random.choice(available_new_components), parent = self, requirements=requirements))
        else:
            return
    

    def is_terminal(self, available_components, requirements):
        available_new_components = self.components.get_all_possible_states(available_components, requirements)
        if (available_new_components is not None and len(available_new_components) == 0):
            return True
        else:
            return False

    
    def get_random_child(self):
        if self.children is not None and len(self.children) > 0:
            return random.choice(self.children)
        else:
            return None

    
    def get_best_child(self):
        best_node = random.choice(self.children)

        for child in self.children:
            if child.get_UCB > child.get_UCB:
                best_node = child

        return best_node

    
    def get_UCB(self):
        return self.score + sqrt(2 * log(self.parent.visit_count) / self.visit_count)


    def calculate_score(self, Requirements = None):
        if self.components.is_complete_state():
            if Requirements is not None:
                if Requirements.performance_weight < Requirements.cost_weight:
                    cost_penalty = Requirements.cost_weight / Requirements.performance_weight
                    performance_penalty = 1 - cost_penalty
                elif Requirements.performance_weight > Requirements.cost_weight:
                    performance_penalty = Requirements.performance_weight / Requirements.cost_weight
                    cost_penalty = 1 - performance_penalty
                else:
                    performance_penalty = 0.5
                    cost_penalty = 0.5
        
                min_cost = 0
                max_cost = 50
                min_ripple_current = 0
                max_ripple_current = 50
                min_ripple_voltage = 0
                max_ripple_voltage = 100

                ripple_voltage_score = 100 / (1 + exp(self.components.get_ripple_voltage() - Requirements.output_voltage * 0.25))
                ripple_voltage_score = (ripple_voltage_score - min_ripple_voltage) / (max_ripple_voltage - min_ripple_voltage)
                ripple_current_score = 100 / (1 + exp(self.components.get_ripple_current() - Requirements.output_current * 0.25))
                ripple_current_score = (ripple_current_score - min_ripple_current) / (max_ripple_current - min_ripple_current)

                if (ripple_voltage_score > 0.95):
                    return 0
                if (ripple_voltage_score > 0.98):
                    return 0

                cost_score = (self.components.get_cost() - min_cost) / (max_cost - min_cost)
                performance_score = performance_penalty * (ripple_current_score + ripple_voltage_score) / 2
                cost_score = cost_penalty * cost_score

                score = 2 - performance_score - cost_score

                return score
        elif len(self.children) > 0:
            return (sum(child.score for child in self.children)) / len(self.children)
        else:
            return 0


class State:

    def __init__(self, Chip = None, Ind = None, Out_Cap = None, In_Cap = None) -> None:
        if Chip:
            self.chip = Chip
        else: 
            self.chip = BuckIC()
        if Ind:
            self.inductor = Ind
        else:
            self.inductor = Inductor()
        if Out_Cap: 
            self.out_cap = Out_Cap
        else:
            self.out_cap = Capacitor()
        if In_Cap:
            self.in_cap = In_Cap
        else:
            self.in_cap = Capacitor()


    def is_complete_state(self):
        if (not (self.chip == BuckIC()) and not (self.inductor == Inductor()) and not (self.out_cap == Capacitor()) and not (self.in_cap == Capacitor())):
            return True
        else:
            return False

    
    def get_all_possible_states(self, available_components = None, requirements = None):
        
        result = []
        if available_components is None or requirements is None:
            return None
        
        if self.chip == BuckIC():
            for ch in available_components.chip_list:
                if (ch.output_voltage == requirements.output_voltage and ch.max_input_voltage >= requirements.max_input_voltage and ch.min_input_voltage <= requirements.min_input_voltage and ch.output_current >= requirements.output_current):
                    result.append(State(Chip = ch))
        elif self.inductor == Inductor():
            for ind in available_components.inductor_list:
                if ind.current_rating >= self.get_peak_current(requirements):
                    result.append(State(Chip = self.chip, Ind = ind))
        elif self.out_cap == Capacitor():
            for cap in available_components.capacitor_list:
                if cap.voltage_rating >= requirements.output_voltage:
                    result.append(State(Chip = self.chip, Ind = self.inductor, Out_Cap = cap))
        elif self.in_cap == Capacitor():
            for cap in available_components.capacitor_list:
                if cap.voltage_rating >= requirements.max_input_voltage:
                    result.append(State(Chip = self.chip, Ind = self.inductor, Out_Cap = self.out_cap, In_Cap = cap))
        
        return result

    
    def get_cost(self):
        return self.chip.cost + self.inductor.cost + self.in_cap.cost + self.out_cap.cost


    def get_ripple_voltage(self):
        return self.get_ripple_current() / (6 * self.out_cap.capacitance * self.chip.switching_frequency)


    def get_ripple_current(self):
        return (self.chip.output_voltage * (1 - self.chip.output_voltage / self.chip.max_input_voltage)) / (self.chip.switching_frequency * self.inductor.inductance)


    def get_peak_current(self, Requirements = None):
        if Requirements is not None:
            return Requirements.output_current + Requirements.output_voltage * (1 - Requirements.output_voltage / Requirements.max_input_voltage ) / (2 * self.inductor.inductance * self.chip.switching_frequency)
        else: 
            return -1

class Available_Components:

    def __init__(self, File_List = None) -> None:
        if Requirements:
            if File_List.chip_file:
                self.chip_list = self.get_chip_list(File_List.chip_file)
            else:
                self.chip_list = None
            if File_List.inductor_file:
                self.inductor_list = self.get_inductor_list(File_List.inductor_file)
            else: 
                self.inductor_list = None
            if File_List.capacitor_file:
                self.capacitor_list = self.get_capacitor_list(File_List.capacitor_file)
            else:
                self.capacitor_list = None

    
    def get_chip_list(self, chip_file):
        chip_list = []
        header = []
        with open(chip_file, encoding = "utf-8-sig") as file:
            csv_reader = reader(file, delimiter = ",")
            header = next(csv_reader)
            for row in csv_reader:
                attr_list = []
                for j,x in enumerate(row):
                    attr_list.append(x)

                out_voltage_string = ''
                for chr in attr_list[header.index("Voltage - Output (Min/Fixed)")]:
                    if (chr != 'V'):
                        out_voltage_string += chr
                    else:
                        break

                out_current_string = ''
                for chr in attr_list[header.index("Current - Output")]:
                    if chr.isdigit() or chr == '.':
                        out_current_string += (chr)
                    else:
                        if (chr == 'A'):
                            current_multiplier = 1
                        elif (chr == 'm'):
                            current_multiplier = 1/1000
                        break
                if out_current_string == '':
                    continue

                min_voltage_string = ''
                for chr in attr_list[header.index("Voltage - Input (Min)")]:
                    if (chr != 'V'):
                        min_voltage_string += chr
                    else:
                        break

                max_voltage_string = ''
                for chr in attr_list[header.index("Voltage - Input (Max)")]:
                    if (chr != 'V'):
                        max_voltage_string += chr
                    else:
                        break

                frequency_string = ''
                freq_multiplier = 1
                for chr in attr_list[header.index("Frequency - Switching")]:
                    if chr.isdigit() or chr == '.':
                        frequency_string += chr
                    else:
                        if (chr == 'k'):
                            freq_multiplier = 1000
                            break
                        elif (chr == 'M'):
                            freq_multiplier = 1000000
                            break
                        elif (chr == 'G'):
                            freq_multiplier = 1000000000
                            break
                        elif (chr != ' '):
                            frequency_string = ''
                            break
                if frequency_string == '':
                    continue

                try:
                    new_chip = BuckIC(id = attr_list[header.index("DK Part #")], 
                                cost = float(attr_list[header.index("Price")]), 
                                min_input_voltage = float(min_voltage_string), 
                                max_input_voltage = float(max_voltage_string), 
                                output_voltage = float(out_voltage_string), 
                                output_current = float(out_current_string) * current_multiplier,
                                switching_frequency= float(frequency_string) * freq_multiplier, 
                                manufacturer=attr_list[header.index("Mfr")], 
                                part_number=attr_list[header.index("Mfr Part #")])
                    chip_list.append(new_chip)
                except:
                    pass
        return chip_list

    def get_inductor_list(self, inductor_file):
        inductor_list = []
        header = []
        with open(inductor_file, encoding = "utf-8-sig") as file:
            csv_reader = reader(file, delimiter = ",")
            header = next(csv_reader)
            for row in csv_reader:
                attr_list = []
                for j,x in enumerate(row):
                    attr_list.append(x)

                current_rating_string = ''
                current_rating_multiplier = 1
                for chr in attr_list[header.index("Current Rating (Amps)")]:
                    if chr.isdigit() or chr == '.':
                        current_rating_string += chr
                    else:
                        if (chr == 'm'):
                            current_rating_multiplier = 1/1000
                            break
                        elif (chr != ' '):
                            current_rating_string = ''
                            break
                if current_rating_string == '':
                    continue

                inductance_string = ''
                ind_multiplier = 1
                for chr in attr_list[header.index("Inductance")]:
                    if chr.isdigit() or chr == '.':
                        inductance_string += chr
                    else:
                        if (chr == 'H'):
                            break
                        elif (chr == 'm'):
                            ind_multiplier = 1/1000
                            break
                        elif (chr == 'µ'):
                            ind_multiplier = 1/1000000
                            break
                        elif (chr == 'n'):
                            ind_multiplier = 1/1000000000
                            break
                        elif (chr != ' '):
                            inductance_string = ''
                            break
                if inductance_string == '':
                    continue

                dcr_string = ''
                dcr_multiplier = 1
                for chr in attr_list[header.index("DC Resistance (DCR)")]:
                    if chr.isdigit() or chr == '.':
                        dcr_string += chr
                    else:
                        if (chr == 'm'):
                            dcr_multiplier = 1/1000
                            break
                        elif (chr != ' '):
                            dcr_string = ''
                            break
                if dcr_string == '':
                    continue

                try:
                    new_inductor = Inductor(id = attr_list[header.index("DK Part #")], 
                                cost = float(attr_list[header.index("Price")]), 
                                current_rating = float(current_rating_string) * current_rating_multiplier,
                                inductance = float(inductance_string) * ind_multiplier, 
                                dc_resistance = float(dcr_string) * dcr_multiplier,
                                manufacturer=attr_list[header.index("Mfr")], 
                                part_number=attr_list[header.index("Mfr Part #")])
                    if all([(new_inductor.inductance != ind.inductance or new_inductor.current_rating != ind.current_rating) for ind in inductor_list]):
                        inductor_list.append(new_inductor)
                except:
                    pass
        return inductor_list


    def get_capacitor_list(self, capacitor_file):
        capacitor_list = []
        header = []
        with open(capacitor_file, encoding = "utf-8-sig") as file:
            csv_reader = reader(file, delimiter = ",")
            header = next(csv_reader)
            for row in csv_reader:
                attr_list = []
                for j,x in enumerate(row):
                    attr_list.append(x)

                voltage_rating_string = ''
                voltage_rating_multiplier = 1
                for chr in attr_list[header.index("Voltage - Rated")]:
                    if chr.isdigit() or chr == '.':
                        voltage_rating_string += chr
                    else:
                        break
                if voltage_rating_string == '':
                    continue

                capacitance_string = ''
                capacitance_multiplier = 1
                for chr in attr_list[header.index("Capacitance")]:
                    if chr.isdigit() or chr == '.':
                        capacitance_string += chr
                    else:
                        if (chr == 'm'):
                            capacitance_multiplier = 1/1000
                            break
                        elif (chr == 'µ'):
                            capacitance_multiplier = 1/1000000
                            break
                        elif (chr == 'n'):
                            capacitance_multiplier = 1/1000000000
                            break
                        elif (chr == 'p'):
                            capacitance_multiplier = 1/1000000000000
                            break
                        elif (chr != ' '):
                            capacitance_string = ''
                            break
                if capacitance_string == '':
                    continue

                try:
                    new_capacitor = Capacitor(id = attr_list[header.index("DK Part #")], 
                                cost = float(attr_list[header.index("Price")]), 
                                voltage_rating = float(voltage_rating_string) * voltage_rating_multiplier,
                                capacitance = float(capacitance_string) * capacitance_multiplier, 
                                manufacturer=attr_list[header.index("Mfr")], 
                                part_number=attr_list[header.index("Mfr Part #")])
                    if all([(new_capacitor.voltage_rating != cap.voltage_rating or new_capacitor.capacitance != cap.capacitance) for cap in capacitor_list]):
                        capacitor_list.append(new_capacitor)
                except:
                    pass

        return capacitor_list

class Solution:
    def __init__(self, nodes = [], iter = 0):
        self.node_list = nodes
        self.iteration_count = iter

@dataclass 
class BuckIC:
    id: str = 'None'
    cost: float = -1
    min_input_voltage: float = -1
    max_input_voltage: float = -1
    output_voltage: float = -1
    output_current: float = -1
    switching_frequency: float = -1
    manufacturer: str = 'None'
    part_number: str = 'None'


@dataclass
class Inductor:
    id: str = 'None'
    cost: float = -1
    inductance: float = -1
    dc_resistance: float = -1
    current_rating: float = -1
    manufacturer: str = 'None'
    part_number: str = 'None'


@dataclass
class Capacitor:
    id: str = 'None'
    cost: float = -1
    capacitance: float = -1
    voltage_rating: float = -1
    manufacturer: str = 'None'
    part_number: str = 'None'


@dataclass
class File_List:
    chip_file : str
    inductor_file : str
    capacitor_file : str