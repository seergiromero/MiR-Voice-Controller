import requests
import json


class Rest_API:
    def __init__(self):
        self.headers = {
            "Authorization": "Basic ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA==",
            "Content-Type": "application/json",
            "Language": "en_US"
            }
        self.url = "http://10.52.17.100/api/v2.0.0/"
        self.positions = {} # Dictionary with the positions names and its guid
        self.missions = {} # Dictionary with the missions names and its guid
    
    def api_request(self, method, endpoint, data = None, custom_url = False):
        """
        Function to automate the process of sending an api_request
        """
        url_complete = endpoint if custom_url else self.url + endpoint
        request_method = {
            'GET': requests.get,
            'POST': requests.post,
            'DELETE': requests.delete,
            'PUT': requests.put
        }
        response = request_method[method](url_complete, headers=self.headers, data=json.dumps(data) if data else None)
        return response

    def get_missions(self):
        """
        Get the missions names from the robot
        """
        response = self.api_request('GET', "missions")
        if response.status_code == 200:
            missions = response.json()  
            self.missions = {mission["name"]: mission["guid"] for mission in missions}
            return self.missions
        else:
            print("Error fetching missions names:", response.status_code)

    def get_positions(self):
        """
        Get all the positions that are configured on the map
        """
        response = self.api_request('GET', "positions")
        if response.status_code == 200:
            positions = response.json()  
            for position in positions:
                if position["type_id"] == 0 and position["map"] == "/v2.0.0/maps/6bad8aa5-b6e0-11ef-9eaa-b46921170fcf":
                    self.positions[position["name"]] = position["guid"] 
            return self.positions
        else:
            print("Error fetching positions:", response.status_code)

    def execute_mission(self, mission_name):
        body = {"mission_id": self.missions[mission_name]}
        response = self.api_request('POST', "mission_queue", body )
        if response.status_code == 201:
            print("Mission '%s' sent successfully to robot" % (mission_name))
        else:
            print("Error sending the mission to the robot:", response.status_code)

    def go_to(self, position_name):
        goto_guid = "mirconst-guid-0000-0001-actionlist00"
        body = {"mission_id": goto_guid,
                "parameters":[
                    {
                        "id": "Position",
                        "value": self.positions[position_name]
                    }
                ]}
        response = self.api_request('POST', 'mission_queue', body)
        if response.status_code == 201:
            print("Robot sent to position '%s'" % (position_name))
        else:
            print("Error sending the mission to the robot:", response.status_code)

    def select_robot(self, robot):
        match robot:
            case "mir200":
                self.url = "http://10.52.17.100/api/v2.0.0/"
                print("MiR200 selected")
            case "mir250":
                self.url = "http://10.52.17.136/api/v2.0.0/"
                print("MiR250 selected")