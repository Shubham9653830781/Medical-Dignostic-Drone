from pymavlink import mavutil
import subprocess
import time
import matplotlib.pyplot as plt
from datetime import datetime

# Constants
CONNECTION_STRING = 'udpin:localhost:14550'
CRUISE_SPEED = 10  # m/s
EARTH_RADIUS = 6378137  # meters
DEGREE_INCREMENT = 0.0001  # ~11 meters
FLIGHT_ALTITUDE = 10
HOLD_TIME = 3  # seconds to stop at each waypoint
ACCEPTANCE_RADIUS = 1  # meters

def connect_drone():
    """Establish connection with the drone"""
    conn = mavutil.mavlink_connection(CONNECTION_STRING)
    conn.wait_heartbeat()
    print(f"Connected to system {conn.target_system} (component {conn.target_component})")
    return conn

def get_current_position(conn):
    """Fetch the drone's current GPS coordinates and velocity in m/s."""
    while True:
        msg = conn.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if msg:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.alt / 1e3
            vx = msg.vx / 1e3
            vy = msg.vy / 1e3
            vz = msg.vz / 1e3
            speed = (vx**2 + vy**2)**0.5
            return {'lat': lat, 'lon': lon, 'alt': alt, 'vx': vx, 'vy': vy, 'vz': vz, 'speed': speed}

def create_initial_waypoints(lat, lon, home_alt):
    """Generate initial waypoints with stopping parameters"""
    waypoints = []
    for i in range(15):
        waypoints.append({
            'lat': lat,
            'lon': lon,
            'alt': FLIGHT_ALTITUDE,
            'command': mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            'hold_time': HOLD_TIME,
            'acceptance_radius': ACCEPTANCE_RADIUS,
            'pass_radius': 0  # Disable pass-through
        })
    
    # Add speed change command as first item
    waypoints.insert(0, {
        'command': mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
        'param1': 1,  # Ground speed
        'param2': CRUISE_SPEED,
        'param3': -1,  # No throttle change
        'param4': 0,   # Absolute speed
        'lat': 0,
        'lon': 0,
        'alt': 0
    })
    
    # Configure landing
    waypoints[-1].update({
        'command': mavutil.mavlink.MAV_CMD_NAV_LAND,
        'alt': home_alt,
        'hold_time': 0,
        'acceptance_radius': 5  # Larger radius for landing
    })
    return waypoints

def set_flight_mode(conn, mode):
    """Set the flight mode with verification"""
    mode_id = conn.mode_mapping()[mode]
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id, 0, 0, 0, 0, 0
    )
    print(f"Switching to {mode} mode...")
    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            raise Exception("Failed to change mode")
        msg = conn.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
        if msg and msg.custom_mode == mode_id:
            print(f"Successfully changed to {mode} mode")
            return

def arm_and_takeoff(conn, altitude):
    """Arm the drone and take off."""
    print("Switching to GUIDED mode")
    set_flight_mode(conn, "GUIDED")

    print("Arming motors")
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,  # Confirmation
        1,  # Param1: 1 to arm
        0, 0, 0, 0, 0, 0  # Params 2-7: Set to 0
    )

    # Wait for arming
    while True:
        msg = conn.recv_match(type='HEARTBEAT', blocking=True)
        if msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
            print("Armed!")
            break
        time.sleep(1)

    # Takeoff
    print(f"Taking off to {altitude}m")
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,  # Confirmation
        0, 0, 0, 0, 0, 0,  # Params 1-6: Set to 0
        altitude  # Param7: Target altitude
    )

def upload_mission(conn, waypoints):
    """Upload mission to the drone with proper stopping parameters"""
    print("Clearing existing mission")
    conn.mav.mission_clear_all_send(conn.target_system, conn.target_component)
    print("Uploading new mission")
    conn.mav.mission_count_send(conn.target_system, conn.target_component, len(waypoints))
    
    for seq in range(len(waypoints)):
        while True:
            msg = conn.recv_match(type=['MISSION_REQUEST', 'MISSION_ACK'], timeout=3)
            if not msg:
                continue
            if msg.get_type() == 'MISSION_REQUEST' and msg.seq == seq:
                wp = waypoints[seq]
                frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
                if wp['command'] == mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED:
                    frame = mavutil.mavlink.MAV_FRAME_MISSION
                
                conn.mav.mission_item_send(
                    conn.target_system, conn.target_component,
                    seq,
                    frame,
                    wp['command'],
                    0,  # Current
                    1,  # Autocontinue
                    wp.get('param1', 0),
                    wp.get('param2', 0),
                    wp.get('param3', 0),
                    wp.get('param4', 0),
                    wp['lat'], wp['lon'], wp['alt']
                )
                break
            elif msg.get_type() == 'MISSION_ACK':
                if msg.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
                    print("Mission upload successful")
                    return True
                else:
                    print(f"Mission upload failed with code {msg.type}")
                    return False

def mode_check(conn):


    while True:
        mode_ck = conn.recv_match(type='HEARTBEAT', blocking=True).base_mode
        if (mode_ck == 89):
            
            break
        time.sleep(1)
    subprocess.run(["python3", "gui.py"])

    return print("The Drone has landed!")




    

# Main Execution
if __name__ == "__main__":
    conn = connect_drone()
    home = get_current_position(conn)

    # Insert Location Coordinates
    lat = -35.36101637
    lon = 149.17035943
    
    waypoints = create_initial_waypoints(lat, lon, home['alt'])
    
    if len(waypoints) > 12:  
        waypoints[-1]['alt'] = home['alt']

    set_flight_mode(conn, "GUIDED")
    arm_and_takeoff(conn, FLIGHT_ALTITUDE)
    time.sleep(8)
    upload_mission(conn, waypoints)
    time.sleep(8)
    set_flight_mode(conn, "AUTO")
    mode_check(conn)
    





    
    
