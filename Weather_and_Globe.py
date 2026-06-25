import math 
#Start Date-23June 2026 for documentation purposes. 
#

class Globe:
    EARTH_RADIUS = 6371000.0  # meters

    G0 = 9.80665

    @staticmethod
    def density(altitude):
         
         altitude = max(0.0, altitude)
         return 1.225 * math.exp(-altitude / 8500.0)

    @staticmethod
    def gravity(altitude):
             return Globe.G0 * (Globe.EARTH_RADIUS /(Globe.EARTH_RADIUS + altitude)) ** 2 # ** means squared
    
#class Weather:
          

    
