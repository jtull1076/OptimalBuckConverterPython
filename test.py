from components import *

file_list = File_List(chip_file = r"C:\Users\jerem\OneDrive\Documents\OSU Coursework\ME617\ChipListNew.csv", inductor_file=r"C:\Users\jerem\OneDrive\Documents\OSU Coursework\ME617\InductorListNew.csv", capacitor_file=r"C:\Users\jerem\OneDrive\Documents\OSU Coursework\ME617\CapacitorListNew.csv")
av_comp = Available_Components(file_list)
print("Number of available chips: ", len(av_comp.chip_list))
print("Number of available inductors: ", len(av_comp.inductor_list))
print("Number of available capacitors: ", len(av_comp.capacitor_list))