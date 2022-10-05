from tkinter import *
from tkinter.font import Font
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename
import ctypes
import sys
from components import Requirements
from tree_search import *
import threading
import time
from PIL import Image, ImageTk

global solution

def file_frame_setup():
    file_frame = Frame(Application, padding="3 3 12 12")
    file_frame.grid(column=0, row=0, sticky=N+S+E+W)
    file_frame.rowconfigure(index = 0, weight = 1)
    file_frame.columnconfigure(index = 0,weight = 1)

    Label(file_frame, text = "List of Buck IC's:").grid(column=0, row=1, sticky = (E))
    Label(file_frame, text = "List of Inductors:").grid(column = 0, row = 2, sticky = (E))
    Label(file_frame, text = "List of Capacitors:").grid(column = 0, row = 3, sticky = (E))

    Entry(file_frame, textvariable = buck_file, text = buck_file).grid(column = 1, row = 1, sticky = N+S+E+W)
    Entry(file_frame, textvariable = inductor_file, text = inductor_file).grid(column = 1, row = 2, sticky = N+S+E+W)
    Entry(file_frame, textvariable = capacitor_file, text = capacitor_file).grid(column = 1, row = 3, sticky = N+S+E+W)
    file_frame.columnconfigure(1, weight=3)

    Button(file_frame, text = "Browse", command = get_buck_file).grid(column = 2, row = 1, sticky = (W,E))
    Button(file_frame, text = "Browse", command = get_ind_file).grid(column = 2, row = 2, sticky = (W,E))
    Button(file_frame, text = "Browse", command = get_cap_file).grid(column = 2, row = 3, sticky = (W,E))

def inputs_frame_setup():
    inputs_frame = Frame(Application, padding="3 3 12 12")
    inputs_frame.grid(column=0, row=1, sticky=(W))
    inputs_frame.rowconfigure(index = 0, weight = 1)
    inputs_frame.columnconfigure(index = 0,weight = 1)

    Label(inputs_frame, text = "Input Voltage (min):").grid(column=1, row=0, sticky = (E))
    Label(inputs_frame, text = "Input Voltage (max):").grid(column = 1, row = 1, sticky = (E))
    Label(inputs_frame, text = "Output Voltage:").grid(column = 1, row = 2, sticky = (E))
    Label(inputs_frame, text = "Output Current:").grid(column=1, row= 3, sticky = (E))
    Label(inputs_frame, text = "Time to Run:").grid(column = 1, row = 4, sticky = (E))

    Entry(inputs_frame, textvariable = min_input_voltage).grid(column = 2, row = 0)
    Entry(inputs_frame, textvariable = max_input_voltage).grid(column = 2, row = 1)
    Entry(inputs_frame, textvariable = output_voltage).grid(column = 2, row = 2)
    Entry(inputs_frame, textvariable = output_current).grid(column = 2, row = 3)
    Entry(inputs_frame, textvariable = run_time).grid(column = 2, row = 4)
    Label(inputs_frame, text = "V").grid(column = 3, row = 0, sticky = W)
    Label(inputs_frame, text = "V").grid(column = 3, row = 1, sticky = W)
    Label(inputs_frame, text = "V").grid(column = 3, row = 2, sticky = W)
    Label(inputs_frame, text = "A").grid(column = 3, row = 3, sticky = W)
    Label(inputs_frame, text = "s").grid(column = 3, row = 4, sticky = W)
    Label(inputs_frame, text = "Priority (Cost vs. Performance):").grid(column = 1, row = 5)
    Label(inputs_frame, text = "Cost").grid(column = 1, row = 6, sticky = E)
    Label(inputs_frame, text = "Performance").grid(column = 3, row = 6)
    Scale(inputs_frame, variable=weight, from_=0, to=10, orient='horizontal').grid(column=2, row=6, sticky = (W,E))

    return inputs_frame

def outputs_frame_setup():
    outputs_frame = Frame(Application, padding="3 3 12 12")
    outputs_frame.grid(column=0, row=2, sticky=(N, W))

    return outputs_frame

def get_buck_file(*args):
    buck_file.set(askopenfilename())

def get_ind_file(*args):
    inductor_file.set(askopenfilename())

def get_cap_file(*args):
    capacitor_file.set(askopenfilename())

def display_info(event, item):
    info_popup = Toplevel(Application)
    for j, (key, value) in enumerate(item.__dict__.items()):
        Label(info_popup, text = key + ": ").grid(row = j, column = 0, sticky = E)
        Label(info_popup, text = value).grid(row = j, column = 1, sticky = W)
    

def solution_popup(value = None):
    global solution
    if value is not None: 
        popup = Toplevel(Application)
        popup.title("Solution Details")
        Label(popup, text= "IC: ").grid(row = 0, column = 0, sticky = E)
        Label(popup, text = "Inductor: ").grid(row = 1, column = 0, sticky = E)
        Label(popup, text = "Output Capacitor: ").grid(row = 2, column = 0, sticky = E)
        Label(popup, text = "Input Capacitor: ").grid(row = 3, column = 0, sticky = E)

        chip = solution.node_list[int(value[-1])].components.chip
        chip_trimmed = chip.id.split(',')[0]
        inductor = solution.node_list[int(value[-1])].components.inductor
        inductor_trimmed = inductor.id.split(',')[0]
        output_cap = solution.node_list[int(value[-1])].components.out_cap
        output_cap_trimmed = output_cap.id.split(',')[0]
        input_cap = solution.node_list[int(value[-1])].components.in_cap
        input_cap_trimmed = input_cap.id.split(',')[0]

        chip_label = Label(popup, text= chip_trimmed)
        chip_label.grid(row = 0, column = 1, sticky = W)
        inductor_label = Label(popup, text = inductor_trimmed)
        inductor_label.grid(row = 1, column = 1, sticky = W)
        outcap_label = Label(popup, text = output_cap_trimmed)
        outcap_label.grid(row = 2, column = 1, sticky = W)
        incap_label = Label(popup, text = input_cap_trimmed)
        incap_label.grid(row = 3, column = 1, sticky = W)
        chip_label.bind("<Button-1>", lambda event, item=chip: display_info(event, item))
        inductor_label.bind("<Button-1>", lambda event, item=inductor: display_info(event, item))
        outcap_label.bind("<Button-1>", lambda event, item=output_cap: display_info(event, item))
        incap_label.bind("<Button-1>", lambda event, item=input_cap: display_info(event, item))

        Label(popup, text = "Cost: ").grid(row = 0, column = 3, sticky = E)
        Label(popup, text = "Score: ").grid(row = 1, column = 3, sticky = E)
        Label(popup, text = "Voltage Ripple: ").grid(row = 2, column = 3, sticky = E)
        Label(popup, text = "Current Ripple: ").grid(row = 3, column = 3, sticky = E)

        Label(popup, text = solution.node_list[int(value[-1])].components.get_cost()).grid(row = 0, column = 4, sticky = W)
        Label(popup, text = solution.node_list[int(value[-1])].score).grid(row = 1, column = 4, sticky = W)
        Label(popup, text = solution.node_list[int(value[-1])].components.get_ripple_voltage()).grid(row = 2, column = 4, sticky = W)
        Label(popup, text = solution.node_list[int(value[-1])].components.get_ripple_current()).grid(row = 3, column = 4, sticky = W)


def options_menu_setup():
    global solution
    dropdown_var = StringVar()
    name_list = []
    for j,item in enumerate(solution.node_list):
        name_list.append(f"Solution #{j+1}")
    dropdown = OptionMenu(outputs_frame, dropdown_var, name_list[0], *name_list, command=solution_popup)
    dropdown.grid(row = 0, column = 0, sticky = W)


def run_search(Requirements, File_List, Run_Time):
    global solution
    if File_List.chip_file != '' and File_List.inductor_file != '' and File_List.capacitor_file != '':
        available_components = Available_Components(File_List)
        if Requirements.min_input_voltage and Requirements.max_input_voltage and Requirements.output_voltage and Requirements.output_current \
        and Run_Time and available_components:
            solution = MCTS(requirements=Requirements, run_time = Run_Time, available_components=available_components)
    else:
        pass


def run_process():
    try:
        requirements = Requirements(min_input_voltage=min_input_voltage.get(), max_input_voltage=max_input_voltage.get(), output_voltage=output_voltage.get(),
                                    output_current=output_current.get(), performance_weight=weight.get() - 5, cost_weight = 5-weight.get())
        file_list = File_List(chip_file=buck_file.get(), inductor_file=inductor_file.get(), capacitor_file=capacitor_file.get() )
        time_to_run = float(run_time.get())
    except ValueError:
        print('Invalid Value')
        return
    
    outputs_frame.columnconfigure(index=1, weight = 5)
    bar = Progressbar(
        outputs_frame, 
        orient='horizontal', 
        mode = 'determinate', 
        length = 400)
    bar.grid(row = 0, column = 1, padx = 5, pady = 5, columnspan = 2, sticky = (W,E))
    
    search_thread = threading.Thread(target=run_search, args=(requirements, file_list, time_to_run))
    search_thread.start()

    start = time.time()
    bar['maximum'] = time_to_run
    while (time.time() - start) < time_to_run:
        bar['value'] = (time.time() - start)
        Application.update()
        time.sleep(0.1)

    search_thread.join()

    bar.grid_remove()
    options_menu_setup()

if __name__ == "__main__":
    if 'win' in sys.platform:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)


Application = Tk()
Application.minsize(1000,500)
Application.title("Automated Circuit Designer")

buck_file = StringVar(value = r"C:\Users\jerem\OneDrive\Documents\OSU Coursework\ME617\ChipListNew.csv")
inductor_file = StringVar(value = r"C:\Users\jerem\OneDrive\Documents\OSU Coursework\ME617\InductorListNew.csv")
capacitor_file = StringVar(value = r"C:\Users\jerem\OneDrive\Documents\OSU Coursework\ME617\CapacitorListNew.csv")

file_frame_setup()

min_input_voltage = DoubleVar(value = 3)
max_input_voltage = DoubleVar(value = 4)
output_voltage = DoubleVar(value = 3.3)
output_current = DoubleVar(value = 1)
run_time = DoubleVar(value = 10)
weight = DoubleVar(value = 5)

inputs_frame = inputs_frame_setup()

image = Image.open("buckconverter.png")
image_tk = ImageTk.PhotoImage(image)
image_label = Label(inputs_frame, image = image_tk)
image_label.grid(row = 0, column = 4, rowspan = 4, sticky = W)

outputs_frame = outputs_frame_setup()

start_button = Button(inputs_frame, text="Run", command = run_process).grid(column = 2, row=7, sticky = (W,E))


for frame in Application.winfo_children():
    frame.grid_configure(padx=5, pady=5)
    for widget in frame.winfo_children():
        widget.grid_configure(padx=3, pady=3)

Application.columnconfigure(0, weight = 1)
Application.columnconfigure(1, weight = 1)
Application.mainloop()

