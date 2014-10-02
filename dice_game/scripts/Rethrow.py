#!/usr/bin/env python

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class Rethrow():

	dices = [0] * 5

	counts = [0] * 7	
	twins = [0] * 6

	to_roll = [False] * 5

	def count(self):
		for i in range(len(self.dices)):
			if(self.dices[i]!=0 and self.dices[i]<7):
				self.counts[self.dices[i]] += 1

	def group(self):
		for i in range(len(self.counts)):
			self.twins[self.counts[i]] += 1

	def calculate(self):
		if(self.twins[5]==1):
			print "CLASS: " +bcolors.OKGREEN + "GENERAL" + bcolors.ENDC

		elif(self.twins[4]==1):
			print "CLASS: " +bcolors.OKGREEN + "QUARTET" + bcolors.ENDC
			for i in range(1,7):
				if(self.counts[i] == 1):
					for j in range(0,5):
						if(self.dices[j] == i):
							self.to_roll[j] = True

		elif(self.twins[3] == 1 and self.twins[2] == 1):
			print "CLASS: " +bcolors.OKGREEN + "FULL" + bcolors.ENDC

		elif(self.twins[3] == 1 and self.twins[2] != 1):
			print "CLASS: " +bcolors.OKGREEN + "TRIPLE" + bcolors.ENDC
			for i in range(1,7):
				if(self.counts[i] == 1):
					for j in range(0,5):
						if(self.dices[j] == i):
							self.to_roll[j] = True

		elif (self.twins[2] == 2):
			print "CLASS: " +bcolors.OKGREEN + "TWO DOUBLES" + bcolors.ENDC
			for i in range(1,7):
				if(self.counts[i] == 1):
					for j in range(0,5):
						if(self.dices[j] == i):
							self.to_roll[j] = True

		elif (self.twins[2] == 1 and self.twins[3] != 1):
			print "CLASS: " +bcolors.OKGREEN + "DOUBLE" + bcolors.ENDC
			for i in range(1,7):
				if(self.counts[i] == 1):
					for j in range(0,5):
						if(self.dices[j] == i):
							self.to_roll[j] = True

		elif (self.twins[2] == 0 and self.twins[3] == 0 and self.twins[4] == 0 and self.twins[5] == 0):
			miss = 1
			for i in range(1,7):
				if(self.counts[i]==0): 
					miss = i			
			if(miss==1 or miss==6):
				print "CLASS: " +bcolors.OKGREEN + "STREET" + bcolors.ENDC
			else:
				print "CLASS: " +bcolors.OKGREEN + "NOTHING" + bcolors.ENDC
				for i in range(0,5):
					if(self.dices[i] == 1):
						self.to_roll[i] = True

		else:
			print "CLASS: " + bcolors.OKGREEN + "UNRECOGNIZED" + bcolors.ENDC

	
	def get_pos_to_roll(self):
		pos_to_roll = []
		for i in range(len(self.to_roll)):
			if(self.to_roll[i]):
				pos_to_roll.append(i)
		for i in pos_to_roll:
			print "RETHROW "+ bcolors.OKGREEN + str(self.dices[i]) + bcolors.ENDC +" on position "+ str(i)
		return pos_to_roll


	def get_decision_vector(self, dices_vector):
		print bcolors.OKGREEN + "[RETHROW DECISION]" + bcolors.ENDC
		self.dices = dices_vector
		print "DICES: " + bcolors.OKGREEN + str(dices_vector) + bcolors.ENDC
		self.count()
		self.group()
		self.calculate()
		return self.get_pos_to_roll()
		



