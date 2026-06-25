############################################################
# Physics Computation Engine for Aircraft Simulation 
############################################################
from Weather_and_Globe import Globe
#from Weather_and_Globe import Weather
import math
import random
from Aircraft_State import AircraftState
import numpy as np


class PhysicsEngine:
    
    def __init__(self, state: AircraftState):

        self.state = state

        ####################################################
        # DYNAMIC FLIGHT STATE
        ####################################################
        self.x = 0.0
        self.y = 0.1
        self.z = 0.0

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0

        self.pitch_rate = 0.0
        self.roll_rate = 0.0
        self.yaw_rate = 0.0

        self.elevator = 0.0
        self.aileron = 0.0
        self.rudder = 0.0
        self.flaps = 0.0

        self.max_elevator = math.radians(25)
        self.max_aileron = math.radians(20)
        self.max_rudder = math.radians(30)
        self.max_flaps = math.radians(40)

        self.control_rate = math.radians(60)

        self.rho0 = 1.225

        self.throttle = 0.0

        self.current_thrust = 0.0

        self.spool_rate = (
        state.engine_spool_rate 
        if state.engine_spool_rate is not None 
        else 0.7
        ) 
        
        self.current_fuel = state.initial_fuel_mass

        self.wind_x = 0.0
        self.wind_y = 0.0
        self.wind_z = 0.0

        self.rho0 = 1.225

        self.max_g = state.max_g
        self.structural_failure = False

    ########################################################
    def update(self, dt):

        if self.structural_failure:
            return

        ####################################################
        # WIND & AIR RELATIVE VELOCITY
        ####################################################
        air_vx = self.vx - self.wind_x
        air_vy = self.vy - self.wind_y
        air_vz = self.vz - self.wind_z

        speed = math.sqrt(air_vx**2 + air_vy**2 + air_vz**2)
        if speed < 0.1:
            speed = 0.1

        side_slip = math.atan2(air_vz, speed)

        rho = Globe.density(self.y)
        gravity = Globe.gravity(self.y)

        flight_path_angle = math.atan2(air_vy, air_vx)
        aoa = self.pitch - flight_path_angle

        ####################################################
        # NONLINEAR STALL MODEL
        ####################################################
        stall_angle = math.radians(15)

        if abs(aoa) < stall_angle:
            CL = self.state.CL0 + self.state.CL_alpha * aoa
        else:
            CL = self.state.CL_max * math.exp(-((abs(aoa) - stall_angle) * 5))

        CD = self.state.CD0 + self.state.k * CL**2

        if abs(aoa) > stall_angle:
            CD *= 3.0

        ####################################################
        # FLAP EFFECTS
        ####################################################
        CL += self.state.flap_effectiveness * self.flaps
        pitch_flap_moment = -0.5 * self.flaps

        ####################################################
        # FORCES
        ####################################################
        Lift = 0.5 * rho * speed**2 * self.state.wing_area * CL
        Drag = 0.5 * rho * speed**2 * self.state.wing_area * CD

        current_mass = self.state.empty_mass + self.current_fuel
        if current_mass <= 0:
            current_mass = 1

        Weight = current_mass * gravity

        ####################################################
        # ENGINE MODEL
        ####################################################
        thrust_altitude_factor = rho / self.rho0
        thrust_speed_factor = max(0.3, 1 - speed / 300)

        target_thrust = (
            self.state.engine_thrust
            * self.throttle
            * thrust_altitude_factor
            * thrust_speed_factor
        )

        self.current_thrust += (
            (target_thrust - self.current_thrust) * self.spool_rate * dt
        )

        Thrust = self.current_thrust

        fuel_used = self.state.fuel_burn_rate * self.throttle * dt
        self.current_fuel -= fuel_used

        if self.current_fuel <= 0:
            self.current_fuel = 0
            self.throttle = 0.0

        ####################################################
        # VECTOR FORCES
        ####################################################
        ux = air_vx / speed
        uy = air_vy / speed
        uz = air_vz / speed

        drag_x = -Drag * ux
        drag_y = -Drag * uy
        drag_z = -Drag * uz

        lift_vertical_x = -Lift * uy
        lift_vertical_y = Lift * ux

        cos_r = math.cos(self.roll)
        sin_r = math.sin(self.roll)

        lift_x = lift_vertical_x
        lift_y = lift_vertical_y * cos_r
        lift_z = lift_vertical_y * sin_r

        thrust_x = Thrust * math.cos(self.pitch) * math.cos(self.yaw)
        thrust_y = Thrust * math.sin(self.pitch)
        thrust_z = Thrust * math.cos(self.pitch) * math.sin(self.yaw)

        Fx = drag_x + lift_x + thrust_x
        Fy = drag_y + lift_y + thrust_y - Weight
        Fz = drag_z + lift_z + thrust_z

        ax = Fx / current_mass
        ay = Fy / current_mass
        az = Fz / current_mass

        self.vx += ax * dt
        self.vy += ay * dt
        self.vz += az * dt

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        ####################################################
        # STRUCTURAL G-LIMIT
        ####################################################
        g_load = Lift / (current_mass * gravity)
        if abs(g_load) > self.max_g:
            self.structural_failure = True

        ####################################################
        # PITCH
        ####################################################
        pitch_moment = (
            self.state.Cm_alpha * aoa
            + self.state.elevator_effectiveness * self.elevator
            + pitch_flap_moment
            - 0.8 * self.pitch_rate
        )

        pitch_torque = (
            pitch_moment
            * 0.5
            * rho
            * speed**2
            * self.state.wing_area
            * self.state.mean_chord
        )

        pitch_acc = pitch_torque / self.state.Iyy
        self.pitch_rate += pitch_acc * dt
        self.pitch += self.pitch_rate * dt

        ####################################################
        # ROLL
        ####################################################
        dihedral_effect = getattr(self.state, "dihedral_effect", 0.1)
        roll_stability = -dihedral_effect * self.roll
        slip_roll_effect = -0.5 * side_slip

        roll_torque = (
            self.state.aileron_effectiveness * self.aileron
            + roll_stability
            + slip_roll_effect
            - 0.6 * self.roll_rate
        ) * 0.5 * rho * speed**2 * self.state.wing_area * self.state.wingspan

        roll_acc = roll_torque / self.state.Ixx
        self.roll_rate += roll_acc * dt
        self.roll += self.roll_rate * dt

        ####################################################
        # YAW
        ####################################################
        yaw_stability = (
            -getattr(self.state, "vertical_tail_effect", 0.2) * side_slip
        )

        yaw_torque = (
            self.state.rudder_effectiveness * self.rudder
            + yaw_stability
            - 0.5 * self.yaw_rate
        ) * 0.5 * rho * speed**2 * self.state.wing_area * self.state.wingspan

        yaw_acc = yaw_torque / self.state.Izz
        self.yaw_rate += yaw_acc * dt
        self.yaw += self.yaw_rate * dt

        ####################################################
        # GROUND PHYSICS
        ####################################################
        if self.y < 0:
            penetration = -self.y
            spring_k = 50000
            damper_c = 8000

            reaction = spring_k * penetration - damper_c * self.vy
            self.vy += reaction / current_mass * dt

            friction = 0.7 * reaction
            self.vx -= friction / current_mass * dt

            self.y = 0

        ####################################################
        # TURBULENCE
        ####################################################
        self.wind_x += random.uniform(-0.5, 0.5) * dt
        self.wind_y += random.uniform(-0.5, 0.5) * dt

