#!/usr/bin/env python
from __future__ import division
import rospy
import numpy
import tf
import tf2_ros
import geometry_msgs.msg
import random


def transform_message_from_matrix(T):
    stamped_shell_msg = geometry_msgs.msg.TransformStamped()
    transform_msg = stamped_shell_msg.transform  # has two vectors. translation (x,y,z), and rotation(x,y,z,w)
    # rot = numpy.append(numpy.append(T2[0:3,0:3],[[0,0,0]],axis=0),[[0],[0],[0],[1]],axis=1) #extract rotation part from matrix
    rot = numpy.append(numpy.append(T[0:3, 0:3], [[0, 0, 0]], axis=0), numpy.transpose([[0, 0, 0, 1]]),
                       axis=1)  # extract rotation part from matrix
    q = tf.transformations.quaternion_from_matrix(rot)
    transform_msg.rotation.x = q[0]
    transform_msg.rotation.y = q[1]
    transform_msg.rotation.z = q[2]
    transform_msg.rotation.w = q[3]
    # transform_msg.rotation = tf.transformations.quaternion_from_matrix(rot)
    q2 = T[0:3, 3]
    transform_msg.translation.x = q2[0]
    transform_msg.translation.y = q2[1]
    transform_msg.translation.z = q2[2]
    return transform_msg


def publish_transforms():
    object_transform = geometry_msgs.msg.TransformStamped()


    object_transform.header.stamp = rospy.Time.now()
    object_transform.header.frame_id = "base_frame"
    object_transform.child_frame_id = "object_frame"
    # Rm = tf.transformations.euler_matrix(0.79, 0.0, 0.79)
    Rm = tf.transformations.quaternion_matrix(tf.transformations.quaternion_from_euler(0.79, 0.0, 0.79))
    Tm = tf.transformations.translation_matrix([0.0, 1.0, 1.0])
    base_T_object = tf.transformations.concatenate_matrices(Rm, Tm)
    object_transform.transform = transform_message_from_matrix(base_T_object)
    #    q1 = tf.transformations.quaternion_from_euler(0.79, 0.0, 0.79)
    #    object_transform.transform.rotation.x = q1[0]
    #    object_transform.transform.rotation.y = q1[1]
    #    object_transform.transform.rotation.z = q1[2]
    #    object_transform.transform.rotation.w = q1[3]
    #    object_transform.transform.translation.x = 0.0
    #    object_transform.transform.translation.y = 1.0
    #    object_transform.transform.translation.z = 1.0
    br.sendTransform(object_transform)
    robot_transform = geometry_msgs.msg.TransformStamped()
    robot_transform.header.stamp = rospy.Time.now()
    robot_transform.header.frame_id = "base_frame"
    robot_transform.child_frame_id = "robot_frame"
    Rm = tf.transformations.quaternion_matrix(tf.transformations.quaternion_about_axis(1.5, zaxis))
    Tm = tf.transformations.translation_matrix([0.0, -1.0, 0.0])
    base_T_robot = tf.transformations.concatenate_matrices(Rm, Tm)
    robot_transform.transform = transform_message_from_matrix(base_T_robot)
    #    q2 = tf.transformations.quaternion_about_axis(1.5, (0,0,1))
    #    robot_transform.transform.rotation.x = q2[0]
    #    robot_transform.transform.rotation.y = q2[1]
    #    robot_transform.transform.rotation.z = q2[2]
    #    robot_transform.transform.rotation.w = q2[3]
    #    robot_transform.transform.translation.x = 0.0
    #    robot_transform.transform.translation.y = -1.0
    #    robot_transform.transform.translation.z = 0.0
    br.sendTransform(robot_transform)

    camera_transform = geometry_msgs.msg.TransformStamped()
    camera_transform.header.stamp = rospy.Time.now()
    camera_transform.header.frame_id = "robot_frame"
    camera_transform.child_frame_id = "camera_frame"

    # finding the rotation matrix such that the camera points at object
    # need to find the coordinates of, first the object wrt to robot frame i.e rob_T_obj : fourth column is the coordinates
    robot_T_object = tf.transformations.concatenate_matrices(tf.transformations.inverse_matrix(base_T_robot), base_T_object)
    object_in_robot = robot_T_object.dot(numpy.transpose([0, 0, 0, 1]))
    object_in_robot = object_in_robot[0:3]
    # second, coordinates of camera wrt the robot frame i.e rob_T_frame : pull out 4th column
    # conventions for cross and dot product: from camera --> object
    cam_translation = [0.0, 0.1, 0.1]  # translation from robot to camera
    robot_T_camera = tf.transformations.translation_matrix(cam_translation)
    camera_in_robot = numpy.transpose(cam_translation)  # the translation part of the matrix

    # doing this from the arbitrary camera axis
    camera_T_robot = tf.transformations.inverse_matrix(robot_T_camera)
    robot_T_base = tf.transformations.inverse_matrix(base_T_robot)
    camera_T_object = tf.transformations.concatenate_matrices(camera_T_robot, robot_T_base, base_T_object)
    object_in_camera = camera_T_object.dot(numpy.transpose([0, 0, 0, 1]))
    object_in_camera = object_in_camera[0:3]
    camera_xaxis = [1, 0, 0]

    camera_object_common_axis = numpy.cross(camera_xaxis, object_in_camera)  # cross product
    nrm = numpy.linalg.norm(camera_object_common_axis)

#    camera_object_common_axis[:] = [x / numpy.linalg.norm(camera_object_common_axis) for x in
#                            camera_object_common_axis]  # normalizing the direction vector
    norm_cam_obj = numpy.linalg.norm(object_in_camera)
    norm_cam_xaxis = numpy.linalg.norm(camera_xaxis)
    theta = numpy.arcsin(numpy.linalg.norm(camera_object_common_axis) / (norm_cam_obj * norm_cam_xaxis))
    #theta = random.random()+ 1.5
    #theta = 1.62335748911
    #theta = 0
    print theta
    Rm = tf.transformations.quaternion_matrix(tf.transformations.quaternion_about_axis(theta, camera_object_common_axis))
    # Rm = tf.transformations.quaternion_matrix(random_unit_quaternion)
    Tm = tf.transformations.translation_matrix(cam_translation)
    Tshell = tf.transformations.concatenate_matrices(Tm, Rm)
    camera_transform.transform = transform_message_from_matrix(Tshell)
    br.sendTransform(camera_transform)

if __name__ == '__main__':
    rospy.init_node('project2_solution')
    origin, xaxis, yaxis, zaxis = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)
    # random_unit_quaternion = [0.186727876017104, 0.366673887285805, 0.641990524678574, 0.646939187080219]
    br = tf2_ros.TransformBroadcaster()
    rospy.sleep(0.5)
while not rospy.is_shutdown():
    publish_transforms()
    rospy.sleep(2)
