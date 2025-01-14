import time
import itertools

url = 'https://www.google.com/maps/place/The+Arcadia+Barbers/@-1.2196278,36.8600582,14z/data=!4m10!1m2!2m1!1sbarber,+kasarani!3m6!1s0x182f155e60ff44f3:0xde8f862b18bb1f0d!8m2!3d-1.2196278!4d36.8961071!15sChBiYXJiZXIsIGthc2FyYW5pWhEiD2JhcmJlciBrYXNhcmFuaZIBC2JhcmJlcl9zaG9w4AEA!16s%2Fg%2F11t_zscf7c?entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D'

coordinates = url.split('@')[-1].split('/')[0]
print(coordinates)
print(float(coordinates.split(',')[1]))