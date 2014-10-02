#!/usr/bin/env python

import sys
# IRPOS path
sys.path.append('/home/tpokorsk/ws_irp6/underlay/src/irp6_robot/irp6_bringup/scripts/IRPOS')

from IRPOS import *
from Rethrow import *

class DiceGame(IRPOS):

	#robot_throw_position_j = [20.673250456947635, -64.32410958225101, -42.00780616747592, -43.441943213839664, 125.14253022492787, 326.4248964541462]
	robot_throw_position_j	= [-0.4444352352822683, -1.735647835528146, 0.14163040859044163, 1.5945075369525465, 0.07174855305306815-1.0, -1.6271269414475789]

	#robot_throw_position_m	= [68.38618888334263, 43.36183260117312, -15.82734378878538, -49.81152231899297, 309.2552392267257, 320.9639550466548]

	robot_throw_position_m	= [-14.985396957623314, 2.0750219476960585, -2.524269697159399, -53.28298220120969, 103.30499122799317, 333.8539097043338]


	irp6p_start_position_j = [-0.27521002214252144, -1.5289544995680513, -0.1881898096507504, 0.1370206153962792, 4.686167293784796, -0.14975967673511772]
	#irp6p_start_position_j = [-0.11423322389275581, -1.5888888406402442, -0.12899521280785461, 0.14205550583165594, 4.685165093003377 -0.12819473215668375]

	#irp6p_start_position_m = [1.3446016557364315, 7.093716211805753, -34.23393514616798, 151.94627028352394, 73.05302477025026, 755.4525022234304]
	#irp6p_start_position_m = [18.863693088479913, 13.351768777756622, -34.464842206206825, 152.32169060562794, 73.37660881357, 723.3831244155858]
	#irp6p_start_position_m = [20.01979918500096, 13.67849441372996, -32.319134423805, 151.310097771172, 70.33868871754868, 720.0593193880878]
	irp6p_start_position_m = [6.116680896539328, 8.65822935329347, -34.55437759683414, 151.310097771172, 70.33868871754868, 745.4779455482828]

	irp6p_under_dices_position_j = [-0.31843674637609237, -1.7804713886411552, 0.04921232341079543, 0.14989591493122556, 4.687251306874901, -0.19300918989115987]

	#irp6p_under_dices_position_m = [3.539004124268902, -30.80802835742831, -35.188979312859274, 151.99496496965457, 73.1048610490345, 751.4626795533713]
	#irp6p_under_dices_position_m = [23.162962634917545, -23.883958148916403, -34.44756344661209, 152.41122599625524, 73.4394406666418, 715.516576410997]
	#irp6p_under_dices_position_m = [24.44787403023577, -21.92674592572996, -38.624310879559715, 151.30852697484522, 70.33868871754868, 712.1142315671592]
	irp6p_under_dices_position_m = [10.57303007565645, -47.39406677205562, -40.13855853859, 151.310097771172, 70.34025951387547, 736.9925037909368]

	cup_xyz_position = None
	put_to_cup_position = None

	under_first_dice = None

	last_dots = None
	last_angle = None
	last_pos_x = None
	last_pos_y = None

	dots_lock = threading.Lock()
	angle_lock = threading.Lock()
	x_lock = threading.Lock()
	y_lock = threading.Lock()

	arr_x = [0.0] * 5
	arr_y = [0.0] * 5
	arr_f = [0.0] * 30
	arr_px = [1.0] * 3
	arr_py = [1.0] * 3

	perfect_angle = 0.0

	dice_init_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] * 5
	dots = [0] * 5

	def __init__(self, nodeName, robotName, jointNumber):
		IRPOS.__init__(self, nodeName, robotName, jointNumber)
		rospy.Subscriber('/dots', Int32, self.dots_callback)
		rospy.Subscriber('/angle', Float32, self.angle_callback)
		rospy.Subscriber('/pos_x', Float32, self.pos_x_callback)
		rospy.Subscriber('/pos_y', Float32, self.pos_y_callback)
		rospy.sleep(1.0)

	#CALLBACKS
	def dots_callback(self, data):
		self.dots_lock.acquire()
		self.last_dots = data.data
		self.dots_lock.release()
	
	def angle_callback(self, data):
		self.angle_lock.acquire()
		self.last_angle = data.data
		self.angle_lock.release()

	def pos_x_callback(self, data):
		self.x_lock.acquire()
		self.last_pos_x = data.data
		self.x_lock.release()

	def pos_y_callback(self, data):
		self.y_lock.acquire()
		self.last_pos_y = data.data
		self.y_lock.release()	

	#GET
	def get_dots(self):
		self.dots_lock.acquire()
		ret = self.last_dots
		self.dots_lock.release()
		return ret
	
	def get_angle(self):
		self.angle_lock.acquire()
		ret = self.last_angle
		self.angle_lock.release()
		return ret

	def get_pos_x(self):
		self.x_lock.acquire()
		ret = self.last_pos_x
		self.x_lock.release()
		return ret

	def get_pos_y(self):
		self.y_lock.acquire()
		ret = self.last_pos_y
		self.y_lock.release()
		return ret

	def vec_push(self, vec, value):
		for i in range(len(vec)-1):
			vec[i] = vec[i+1]
		vec[-1] = value

	def vec_mean(self, vec):
		return sum(vec)/len(vec)

	def push_x(self, value):
		for i in range(len(self.arr_x)-1):
			self.arr_x[i] = self.arr_x[i+1]
		self.arr_x[-1] = value	

	def push_y(self, value):
		for i in range(len(self.arr_y)-1):
			self.arr_y[i] = self.arr_y[i+1]
		self.arr_y[-1] = value

	def push_f(self, value):
		for i in range(len(self.arr_f)-1):
			self.arr_f[i] = self.arr_f[i+1]
		self.arr_f[-1] = value

	def mean_x(self):
		return sum(self.arr_x)/len(self.arr_x)

	def mean_y(self):
		return sum(self.arr_y)/len(self.arr_y)	

	def mean_f(self):
		return sum(self.arr_f)/len(self.arr_f)	



def one_dice_loop(number_of_dices):
	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))
	
	rospy.sleep(1.0)
	
	start_position(irpos)
	for i in range(0, number_of_dices): 
		under_dices(irpos)	
		watch_and_go(irpos)
		get_angle(irpos)
		servovision_c(irpos)	
		go_down(irpos)
		tool_corection(irpos)
		save_position(irpos, i)	
		pick_dice(irpos)
		put_to_cup(irpos)
	
	throw_dices(irpos)

	for i in range(0, number_of_dices): 	
		watch_and_go(irpos)
		get_angle(irpos)
		servovision_c(irpos)
		go_down(irpos)
		recive_data(irpos, i)
		tool_corection(irpos)
		turn_gripper(irpos)
		pick_dice(irpos)
		put_away(irpos, i)
		start_position(irpos)

	print "DOTS: " + '\033[92m'+ str(irpos.dots) + '\033[0m'

	return "test compleated"

def trj_test():

	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	rospy.sleep(1.0)

	start_position(irpos)
	#under_dices(irpos)
	#throw_position(irpos)
	#irpos.move_rel_to_joint_position([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 5.0)
	#irpos.move_rel_to_motor_position([0.0, 0.0, 0.0, 0.0, 0.0, 1000.0], 15.0)

	irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(-0.1, 0.0, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))
	#irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.0, 0.14, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))
	#irpos.move_rel_to_joint_position([0.0, 0.0, 0.0, 0.0, 0.0, -8.0*3.14/180.0], 5.0)

	#print str(irpos.get_joint_position())
	print str(irpos.get_motor_position())

	#turn_gripper(irpos)

	#under_dices(irpos)
	#throw_position(irpos)

	return "test compleated"

def turn_test():

	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	rospy.sleep(1.0)

	start_position(irpos)
	turn_gripper(irpos)

	return "test compleated"

def force_test():

	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	start_position(irpos)

	for i in range(0,5):

		irpos.start_force_controller(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.0, 0.0, 0.0025), Vector3(0.0, 0.0, 0.05)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(0.0, 0.0, 0.01), Vector3(0.0, 0.0, 0.0)))

		time.sleep(5.0)

		irpos.stop_force_controller()

		irpos.start_force_controller(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.0, 0.0, 0.0025), Vector3(0.0, 0.0, 0.05)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(0.0, 0.0, -0.01), Vector3(0.0, 0.0, 0.0)))

		time.sleep(5.0)

		irpos.stop_force_controller()

	return "test compleated"

def pick_test(pos):

	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	rospy.sleep(1.0)
	
	if(pos==1):
		start_position(irpos)
	elif(pos==2):
		under_dices(irpos)
	elif(pos==3):
		under_dices(irpos)
	elif(pos==4):
		start_position(irpos)
		tool_corection(irpos)
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0.1, 0.0, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))

	pick_dice(irpos)

	#print str(irpos.get_cartesian_pose())	

	return "test compleated"

def get_position_test():
	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	rospy.sleep(1.0)
	print str(irpos.get_joint_position())
	print str(irpos.get_motor_position())
	print str(irpos.get_cartesian_pose())

def start_pos():
	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	rospy.sleep(1.0)
	start_position(irpos)
	#irpos.move_rel_to_cartesian_pose(5.0, Pose(Point(-0.15, 0.0, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))

	print str(irpos.get_motor_position())
	print str(irpos.get_cartesian_pose())
	#under_dices(irpos)
	#print str(irpos.get_motor_position())

	#throw_position(irpos)
	
	#irpos.move_rel_to_cartesian_pose(5.0, Pose(Point(0.15, -0.15, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))

	return "test compleated"

def quick_test():
	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))
	
	start_position(irpos)
	
	wrench_const = Wrench()
	wrench_const.force.z = 	3.5

	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0.0, 0.0, -0.08), Quaternion(0.0, 0.0, 0.0, 0.0)), wrench_const)
	
	return "test compleated"

def decision_test():

	dots_vec = [1,3,5,2,4]
	make_decision(dots_vec)
	return "test compleated"	

def watch_and_go_test():
	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	rospy.sleep(1.0)
	start_position(irpos)

	watch_and_go(irpos)
	servovision_c(irpos)
	get_angle(irpos)	
	go_down(irpos)
	recive_data(irpos, 0)
	tool_corection(irpos)
	turn_gripper(irpos)	
	pick_dice(irpos)

	return "test compleated"


def full_game():
	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))
	
	rospy.sleep(1.0)
	number_of_dices = 5	

	start_position(irpos)
	for i in range(0, number_of_dices): 
		under_dices(irpos)	
		watch_and_go(irpos)
		get_angle(irpos)
		servovision_c(irpos)	
		go_down(irpos)
		tool_corection(irpos)
		save_position(irpos, i)	
		pick_dice(irpos)
		put_to_cup(irpos)
	
	throw_dices(irpos)

	for i in range(0, number_of_dices): 	
		watch_and_go(irpos)
		get_angle(irpos)
		servovision_c(irpos)
		go_down(irpos)
		recive_data(irpos, i)
		tool_corection(irpos)
		turn_gripper(irpos)
		pick_dice(irpos)
		put_away(irpos, i)
		start_position(irpos)

	dices_to_throw = make_decision(irpos.dots)

	for i in dices_to_throw:
		under_slot(irpos, i)
		pick_dice(irpos)
		put_to_cup(irpos)

	throw_dices(irpos)

	for i in dices_to_throw: 	
		watch_and_go(irpos)
		get_angle(irpos)
		servovision_c(irpos)
		go_down(irpos)
		recive_data(irpos, i)
		tool_corection(irpos)
		turn_gripper(irpos)
		pick_dice(irpos)
		put_away(irpos, i)
		start_position(irpos)

	print "DOTS:" + '\033[92m'+ "[ " + str(irpos.dots[i])+" ]" + '\033[0m'

	return "Dice Game compleated"

def graph_test():

	irpos = DiceGame("IRpOS_Dice_Game", "Irp6p", 6)
	
	rospy.sleep(1.0)
	
	for i in range(0,5):
		irpos.move_rel_to_motor_position([0.0, 0.0, 0.0, 0.0, 0.0, 600.0], 6.0)
		irpos.move_rel_to_motor_position([0.0, 0.0, 0.0, 0.0, 0.0, -600.0], 6.0)
	return "test end"



#######################################

def start_position(irpos):
	print "Set start position"
	
	#irpos.move_to_motor_position(irpos.robot_start_position, 10.0)
	#irpos.move_to_joint_position(irpos.irp6p_start_position_j, 10.0)
	irpos.move_to_motor_position(irpos.irp6p_start_position_m, 12.0)
	align_tool(irpos)

	return 0

def under_dices(irpos):
	print "Go under dices"
	#track
	#irpos.move_to_motor_position([-47.1238898038469, 30.350926626330992, -43.331987470964016, -36.82417828905276, 160.2353625000206-8.0, 111.18574209188958, 712.49122268559], 2.0)
	#irpos.move_to_motor_position(irpos.robot_under_dices_position, 2.0)
	#irpos.move_to_joint_position(irpos.irp6p_under_dices_position_j, 4.0)

	irpos.move_to_motor_position(irpos.irp6p_under_dices_position_m, 6.0)	

	#irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.0, 0.0, 0.025), Quaternion(0.0, 0.0, 0.0, 0.0)))
	align_tool(irpos)
	return 0

def align_tool(irpos):
	print "Align tool"
	align_position = irpos.get_cartesian_pose().position
	align_position.z += 0.02
	irpos.move_to_cartesian_pose(2.0, Pose(align_position, Quaternion(0.707106, 0.707106, 0.0, 0.0)))
	#irpos.move_rel_to_motor_position([0.0, 0.0, 0.0, 0.0, -3.0, 0.0], 3.0)
	

def throw_position(irpos):
	print "Throw position"

	#irpos.move_to_joint_position([-0.03, -0.23531350406490387, -1.915322138595878, 0.135866150284756, 1.794095611681742, 1.4702524084450372, 1.5567201773841515], 6.0)
	#track
	#irpos.move_to_motor_position([-47.1238898038469, 20.673250456947635, -64.32410958225101, -42.00780616747592, -43.441943213839664, 165.14253022492787, 1219.4248964541462], 10.0)
	#irpos.move_to_motor_position(irpos.robot_throw_position, 10.0)
	#irpos.move_to_joint_position([0.0, -1.5418065817051163, 0.0, 1.5, 1.57, -1.57], 10.0)
	#irpos.move_to_joint_position(irpos.robot_throw_position_j, 10.0)
	irpos.move_to_motor_position(irpos.robot_throw_position_m, 12.0)

	#align_position = irpos.get_cartesian_pose().position
	#irpos.move_to_cartesian_pose(2.0, Pose(align_position, Quaternion(0.5, 0.5, 0.5, 0.5)))

def under_cup(irpos):
	move_abs_xyz(irpos, irpos.cup_xyz_position, 6.0)
	return 0


def move_abs_xyz(irpos, position, time):
	print "Move XYZ!"
	irpos.move_to_cartesian_pose(time, Pose(position, irpos.get_cartesian_pose().orientation))

# CARTESIAN SERVO
def servovision_c(irpos):
	print "Run servovision"
	print "Vector: ["+str(irpos.get_pos_x())+", "+str(irpos.get_pos_y())+"]"
	
	time.sleep(2.0)

	max_speed = 0.006
	multiplier = 0.02

	irpos.arr_x = [0.0] * 5
	irpos.arr_y = [0.0] * 5
	irpos.arr_px = [1.0] * 3
	irpos.arr_py = [1.0] * 3

	while(fabs(irpos.vec_mean(irpos.arr_px)) > 0.02 or fabs(irpos.vec_mean(irpos.arr_py)) > 0.02):
		new_px = irpos.get_pos_x()
		new_py = irpos.get_pos_y()	

		irpos.vec_push(irpos.arr_x, new_px)
		irpos.vec_push(irpos.arr_y, new_py)
		irpos.vec_push(irpos.arr_px, new_px)
		irpos.vec_push(irpos.arr_py, new_py)

		if(fabs(new_px) > 0.01 or fabs(new_py) > 0.01):

			vec_x = -irpos.vec_mean(irpos.arr_x)*multiplier
			if(vec_x > max_speed):
				vec_x = max_speed
			elif(vec_x < -1.0*max_speed):
				vec_x = -1.0*max_speed

			vec_y = irpos.vec_mean(irpos.arr_y)*multiplier
			if(vec_y > max_speed):
				vec_y = max_speed
			elif(vec_y < -1.0*max_speed):
				vec_y = -1.0*max_speed

			irpos.move_rel_to_cartesian_pose(0.2, Pose(Point(-vec_x, -vec_y, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))
			print "POS:"+str(new_px)+":"+str(new_py)+"|VEC:"+str(vec_x)+":"+str(vec_y)
		rospy.sleep(0.25)

	return 0

def watch_and_go(irpos):
	print "Run watch&go"
	print "Vector: ["+str(irpos.get_pos_x())+", "+str(irpos.get_pos_y())+"]"
	
	time.sleep(2.0)
	
	if(irpos.get_pos_x()==0.0 and irpos.get_pos_y()==0.0):
		time.sleep(3.0)

	max_speed = 0.4
	#multiplier = 0.2
	multiplier = 0.25
	ttime = 1.0

	irpos.arr_x = [0.0] * 1
	irpos.arr_y = [0.0] * 1
	irpos.arr_px = [1.0] * 1
	irpos.arr_py = [1.0] * 1

	if(fabs(irpos.vec_mean(irpos.arr_px)) > 0.01 or fabs(irpos.vec_mean(irpos.arr_py)) > 0.01):
		new_px = irpos.get_pos_x()
		new_py = irpos.get_pos_y()	

		irpos.vec_push(irpos.arr_x, new_px)
		irpos.vec_push(irpos.arr_y, new_py)
		irpos.vec_push(irpos.arr_px, new_px)
		irpos.vec_push(irpos.arr_py, new_py)

		if(fabs(new_px) > 0.01 or fabs(new_py) > 0.01):

			vec_x = -irpos.vec_mean(irpos.arr_x)*multiplier
			if(vec_x > max_speed):
				vec_x = max_speed
			elif(vec_x < -1.0*max_speed):
				vec_x = -1.0*max_speed

			vec_y = irpos.vec_mean(irpos.arr_y)*multiplier
			if(vec_y > max_speed):
				vec_y = max_speed
			elif(vec_y < -1.0*max_speed):
				vec_y = -1.0*max_speed

			ttime = sqrt((vec_x*vec_x)+(vec_y*vec_y))*30.0
			if(ttime < 0.1):
				ttime = 0.1
			irpos.move_rel_to_cartesian_pose(ttime, Pose(Point(-vec_x, -vec_y, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))
			print "POS:"+str(new_px)+":"+str(new_py)+"|VEC:"+str(vec_x)+":"+str(vec_y)
		rospy.sleep(ttime+0.05)

	return 0

# FORCE SERVO
def servovision_f(irpos):
	print "Run servovision"
	print "Vector: ["+str(irpos.get_pos_x())+", "+str(irpos.get_pos_y())+"]"
	
	irpos.start_force_controller(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.002, 0.002, 0.002), Vector3(0.05, 0.05, 0.05)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))

	while(fabs(irpos.vec_mean(irpos.arr_px)) > 0.01 or fabs(irpos.vec_mean(irpos.arr_py)) > 0.01):
		irpos.push_x(irpos.get_pos_x())
		irpos.push_y(irpos.get_pos_y())
		irpos.vec_push(irpos.arr_px, irpos.get_pos_x())
		irpos.vec_push(irpos.arr_py, irpos.get_pos_y())
		max_speed = 0.05

		vec_x = -irpos.mean_x()*0.05
		if(vec_x > max_speed):
			vec_x = max_speed
		elif(vec_x < -1.0*max_speed):
			vec_x = -1.0*max_speed

		vec_y = irpos.mean_y()*0.05
		if(vec_y > max_speed):
			vec_y = max_speed
		elif(vec_y < -1.0*max_speed):
			vec_y = -1.0*max_speed

		irpos.set_force_controller_goal(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.002, 0.002, 0.002), Vector3(0.05, 0.05, 0.05)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(vec_y, vec_x, 0.0), Vector3(0.0, 0.0, 0.0)))
		time.sleep(0.1)
		print "POS:"+str(irpos.get_pos_x())+":"+str(irpos.get_pos_y())+"|VEC:"+str(vec_x)+":"+str(vec_y)
	irpos.stop_force_controller()
	return 0


def tool_corection(irpos):
	print "Tool corection"
	# cofnij,prawo,gora 
	#irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(-0.01, 0.05, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(-0.01, 0.048, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))
	return 0	
	
def go_down(irpos):
	if(irpos.under_first_dice==None):
		irpos.under_first_dice = irpos.get_joint_position()
	irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.0, 0.0, -0.18), Quaternion(0.0, 0.0, 0.0, 0.0)))

def save_position(irpos, i):
	print "Save position of "+str(i)
	if (irpos.cup_xyz_position == None):
		irpos.cup_xyz_position = irpos.get_cartesian_pose().position
		irpos.put_to_cup_position = Point(irpos.cup_xyz_position.x, irpos.cup_xyz_position.y, irpos.cup_xyz_position.z)	
		
		irpos.cup_xyz_position.x -= 0.02
		irpos.cup_xyz_position.y -= 0.29 #35cm
		irpos.cup_xyz_position.z += 0.13

		irpos.put_to_cup_position.x += 0.0
		irpos.put_to_cup_position.y -= 0.27
		irpos.put_to_cup_position.z += 0.13

		print str(irpos.cup_xyz_position)

	position = irpos.get_motor_position()
	irpos.dice_init_positions[i] = position
	print "Position: " + str(irpos.dice_init_positions[i]) + " saved"


def under_slot(irpos, i):
	print "Go under slot "+str(i)
	#under_dices(irpos)
	irpos.move_to_motor_position(irpos.dice_init_positions[i], 9.0)
	
def pick_dice(irpos):
	print "Pick dice"

	irpos.tfg_to_joint_position(0.085, 3.0)

	irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))

	down_till_contact_c(irpos)

	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0.0, 0.0, 0.005), Quaternion(0.0, 0.0, 0.0, 0.0)))

	irpos.tfg_to_joint_position(0.054, 3.0)

	irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.0, 0.0, 0.1), Quaternion(0.0, 0.0, 0.0, 0.0)))

	return 0
	
def put_to_cup(irpos):
	print "Put tu cup"
	if(irpos.put_to_cup_position != None): 
		move_abs_xyz(irpos, irpos.put_to_cup_position, 3.0)
	irpos.tfg_to_joint_position(0.085, 3.0)

	return 0

def throw_dices(irpos):
	print "Throwing dices"

	under_dices(irpos)
	throw_position(irpos)
	if(irpos.cup_xyz_position != None): 
		under_cup(irpos)
	irpos.tfg_to_joint_position(0.085, 3.0)

	#irpos.start_force_controller(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.0015, 0.0015, 0.0015), Vector3(0.05, 0.05, 0.05)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(-0.02, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))
	#time.sleep(5.0)
	#irpos.stop_force_controller()
	#irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.02, 0.0, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))

	#w dol
	wrench_const = Wrench()
	wrench_const.force.x = 	3.5
	
	irpos.move_rel_to_cartesian_pose_with_contact(10.0, Pose(Point(0.0, 0.0, -0.2), Quaternion(0.0, 0.0, 0.0, 0.0)), wrench_const)

	#zacisnij
	irpos.tfg_to_joint_position(0.063, 3.0)

	#w gore
	irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.0, 0.0, 0.1), Quaternion(0.0, 0.0, 0.0, 0.0)))

	m_position = irpos.get_motor_position()

	#do rzutu
	#irpos.move_rel_to_motor_position([0.0, 0.0, 0.0, 0.0, 56.0, 0.0], 4.0)
	
	#irpos.move_rel_to_cartesian_pose(10.0, Pose(Point(-0.1, -0.02, -0.12), Quaternion(0.0, 0.0, 0.0, 0.0)))

	irpos.move_rel_to_cartesian_pose(10.0, Pose(Point(0.2, 0.2, 0.1), Quaternion(0.0, 0.0, 0.0, 0.0)))
	irpos.move_rel_to_cartesian_pose(10.0, Pose(Point(0.0, 0.4, 0.0), Quaternion(0.0, 0.0, 0.0, 0.0)))
	irpos.move_rel_to_cartesian_pose(10.0, Pose(Point(0.0, 0.0, -0.15), Quaternion(0.0, 0.0, 0.0, 0.0)))

	#rzut - obrot
	irpos.move_rel_to_motor_position([0.0, 0.0, 0.0, 0.0, 0.0, 650.0], 10.0)
	#irpos.move_rel_to_motor_position([0.0, 0.0, 0.0, 0.0, 0.0, 0.5], 3.0)


	irpos.move_rel_to_cartesian_pose(10.0, Pose(Point(0.0, 0.0, 0.15), Quaternion(0.0, 0.0, 0.0, 0.0)))

	irpos.move_to_motor_position(m_position, 20.0)

	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0.0, 0.0, -0.1), Quaternion(0.0, 0.0, 0.0, 0.0)), wrench_const)
	#irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.0, 0.0, -0.095), Quaternion(0.0, 0.0, 0.0, 0.0)))
	#put_cup_till_contact(irpos)

	irpos.tfg_to_joint_position(0.085, 3.0)

	irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.0, 0.0, 0.2), Quaternion(0.0, 0.0, 0.0, 0.0)))

	start_position(irpos)

	return 0
	
def recive_data(irpos, i):
	print "Saving data of "+str(i)
	dots_data = 0
	time.sleep(1.0)
	for j in range(0,5):
		dots_data = irpos.get_dots()
		if(dots_data>irpos.dots[i] and dots_data<=6):
			irpos.dots[i] = dots_data
		time.sleep(0.2)
	print "DOTS:" + '\033[92m'+ "[ " + str(irpos.dots[i])+" ]" + '\033[0m'
	return 0
	
def get_angle(irpos):
	print "Get angle"

	time.sleep(1.5)
	angle = irpos.get_angle()

	degree = 3.14/180

	if(angle > 0.0 and angle<3.14):
		irpos.perfect_angle = angle

	print "ANGLE:" + str(angle)

def turn_gripper(irpos):
	print "Turning gripper"

	time = irpos.perfect_angle * 8.0

	irpos.move_rel_to_joint_position([0.0, 0.0, 0.0, 0.0, 0.0, irpos.perfect_angle], time)
	return 0
	
def put_away(irpos, i):
	print "Putting away to position "+str(i)
	#under_dices(irpos)
	irpos.move_to_motor_position(irpos.dice_init_positions[i], 10.0)

	down_till_contact_f(irpos)

	irpos.tfg_to_joint_position(0.085, 3.0)
	
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0.0, 0.0, 0.03), Quaternion(0.0, 0.0, 0.0, 0.0)))
	under_dices(irpos)

	
	return 0
	
def down_till_contact_f(irpos):
	force_limit = 5.0

	irpos.arr_f = [0.0] * 30
	irpos.start_force_controller(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.0, 0.0, 0.002), Vector3(0.0, 0.0, 0.05)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(0.0, 0.0, 0.01), Vector3(0.0, 0.0, 0.0)))
	time.sleep(0.1)
	counter = 0
	old_reading = None
	last_reading = None
	while(counter < 30 or irpos.mean_f() < force_limit):
		counter += 1
		old_reading = last_reading
		last_reading = irpos.get_force_readings()
		if(last_reading != None and old_reading != None):
			if(last_reading.force.z != old_reading.force.z):
				irpos.push_f(last_reading.force.z)
				print 'FORCE Z = ' + str(last_reading.force.z)
	print 'COUNTER: '+str(counter)
	irpos.stop_force_controller()

def down_till_contact_c(irpos):

	wrench_const = Wrench()
	wrench_const.force.z = 	3.5

	irpos.move_rel_to_cartesian_pose_with_contact(10.0, Pose(Point(0.0, 0.0, -0.25), Quaternion(0.0, 0.0, 0.0, 0.0)), wrench_const)


def put_cup_till_contact(irpos):
	force_limit = -5.0

	irpos.arr_f = [0.0] * 30
	irpos.start_force_controller(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.002, 0.0, 0.0), Vector3(0.05, 0.0, 0.0)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(-0.02, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))
	time.sleep(0.1)
	counter = 0
	old_reading = None
	last_reading = None
	while(counter < 30 or irpos.mean_f() > force_limit):
		counter += 1
		old_reading = last_reading
		last_reading = irpos.get_force_readings()
		if(last_reading != None and old_reading != None):
			if(last_reading.force.x != old_reading.force.x):
				irpos.push_f(last_reading.force.x)
				print 'FORCE X = ' + str(last_reading.force.x)
	print 'COUNTER: '+str(counter)
	irpos.stop_force_controller()

def make_decision(dots_vector):
	decision = Rethrow()
	return decision.get_decision_vector(dots_vector)


if __name__ == '__main__':
	full_game()
	#print one_dice_loop(5)
	#print turn_test()
	#print trj_test()
	#print start_pos()
	#print get_position_test()
	#print watch_and_go_test()
	#print force_test()	
	#print pick_test(1)
	#print quick_test()
	#print decision_test()
	#print graph_test()

