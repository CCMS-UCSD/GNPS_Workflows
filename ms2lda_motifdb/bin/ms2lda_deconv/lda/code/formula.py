import re

class Formula(object):
	def __init__(self,formula):
		self.atom_names = ['C','H','N','O','P','S','Cl','I','Br','Si','F','D']
		self.formula = formula
		self.atoms = {}
		for atom in self.atom_names:
			self.atoms[atom] = self.get_atoms(atom)


	def equals(self,formula):
		is_equal = True
		for atom in self.atoms:
			if not self.atoms[atom] == formula.atoms[atom]:
				is_equal = False
				return is_equal
		return is_equal

	def correct_gcms_derivatives(self):
		n_silicons = self.atoms['Si']
		self.atoms['Si'] = 0
		self.atoms['C'] -= n_silicons
		self.atoms['H'] -= 3*n_silicons
		self.atoms['H'] += n_silicons
		self.make_string()

	def make_string(self):
		self.formula = ""
		for atom in self.atom_names:
			atom_no = self.atoms[atom]
			if atom_no == 1:
				self.formula += atom
			elif atom_no > 1:
				self.formula += atom + str(atom_no)


	def get_atoms(self,atom_name):
		# Do some regex matching to find the numbers of the important atoms
		ex = atom_name + '(?![a-z])' + '\d*'
		m = re.search(ex,self.formula)
		if m == None:
			return 0
		else:
			ex = atom_name + '(?![a-z])' + '(\d*)'
			m2 = re.findall(ex,self.formula)
			total = 0
			for a in m2:
				if len(a) == 0:
					total += 1
				else:
					total += int(a)
			return total

	def compute_exact_mass(self):
		masses = {'C':12.00000000000,'H':1.00782503214,'O':15.99491462210,'N':14.00307400524,'P':30.97376151200,'S':31.97207069000,'Cl':34.96885271000,'I':126.904468,'Br':78.9183376,'Si':27.9769265327,'F':18.99840320500,'D':2.01410177800}
		exact_mass = 0.0
		for a in self.atoms:
			exact_mass += masses[a]*self.atoms[a]
		return exact_mass

	def __str__(self):
		fstring = ""
		for atom in self.atom_names:
			if self.atoms[atom] > 0:
				fstring += atom
			if self.atoms[atom] > 1:
				fstring += str(self.atoms[atom])

		return fstring

	def __repr__(self):
		return self.__str__()
