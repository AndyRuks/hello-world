#!/usr/bin/env python  
import rospy

from std_msgs.msg import Int16
from std_msgs.msg import String
from project1_solution.msg import TwoInts

print "started the solution..."
rospy.init_node('solution_nodes',anonymous = True)
# In ROS, nodes are uniquely named. If two nodes with the same
# name are launched, the previous one is kicked off. The
# anonymous=True flag means that rospy will choose a unique
# name for our 'listener' node so that multiple listeners can
# run simultaneously.
#rospy.init_node('sum_talker', anonymous=True)

def listener():
    print "In the listener..."
    rospy.Subscriber('two_ints',TwoInts, talker)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

def callback(data):
    print "In the callback..."
    sum_value = data.a + data.b # get the sum somehow (two ways 1) pointer reference/global var 2)pass through function
    #rospy.loginfo(rospy.get_caller_id() + "I received %d + %d = ", data.a, data.b, sum_value)
    s =  repr(data.a) + '+' + repr(data.b) + '=' + repr(sum_value)
    print(s)

def talker(data):
    print "In the talker..."
    rate = rospy.Rate(10) #10 Hz
    pub = rospy.Publisher('two_ints',TwoInts, queue_size=10)
    sum_value = data.a + data.b
    s =  repr(data.a) + '+' + repr(data.b) + '=' + repr(sum_value)

    while not rospy.is_shutdown():       
        pub.publish(sum_value)
        print "In the while of the talker, about to print and log info..."
        print(s)
        rospy.loginfo(s)
        rate.sleep()


if __name__ == '__main__':
    try:
        listener()
        #talker()
    except rospy.ROSInterruptException:
        pass
        

