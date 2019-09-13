
import ming_psm_library
import re

def transform_peptide_to_msp_library_string(input_peptide):
    stripped_sequence = input_peptide.replace("+15.5994", "(O)").replace(".", "").replace("-", "").replace("+", "")
    stripped_sequence = re.sub('\d', '', stripped_sequence)

    return stripped_sequence

#Assuming Inspect format
def transform_peptide_to_msp_mods(input_peptide):
    all_atoms = ming_psm_library.get_peptide_modification_list_inspect_format(input_peptide)

    mod_list = []

    index = -1
    for atom in all_atoms:
        index += 1

        #Not a mod
        if atom.find("-") == -1 and atom.find("+") == -1:
            continue

        #N-term only
        if atom[0] == "-" or atom[0] == "+":
            mod_string = str(0) + "," + all_atoms[index][-1] + "," + string_to_msp_name(atom)
            mod_list.append(mod_string)
            continue

        #Normal Mods
        mod_string = str(index) + "," + all_atoms[index][0] + "," + string_to_msp_name(atom)
        mod_list.append(mod_string)

    if len(mod_list) == 0:
        return "0"

    return str(len(mod_list)) + "/" +  "/".join(mod_list)


def string_to_msp_name(input_mod):
    if input_mod.find("+15.995") != -1:
        return "Oxidation"

    if input_mod.find("+57.021") != -1:
        return "Carbamidomethyl"

    if input_mod.find("+42.011") != -1:
        return "Acetyl"

    if input_mod.find("+0.984") != -1:
        return "Deamidation"

    if input_mod.find("+14.016") != -1:
        return "Methyl"

    if input_mod.find("-17.027") != -1:
        return "Pyro_glu"

    if input_mod.find("-18.011") != -1:
        return "Pyro-glu"

    if input_mod.find("+43.006") != -1:
        return "Carbamyl"

    print("Not Valid Modification")
    exit(1)
