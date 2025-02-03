from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union, Callable, TypedDict, Any
import requests
from requests import Response
import json
from urllib.parse import urljoin

class RobotType(Enum):
    SUPERMAN = ("mir200", "http://10.52.17.100/api/v2.0.0/")
    BATMAN = ("mir250", "http://10.52.17.21/api/v2.0.0/")

class Position(TypedDict):
    guid: str
    url: str
    name: str
    map: str
    type_id: int
    
class Mission(TypedDict):
    name: str
    guid: str

@dataclass
class MissionParameter:
    id: str
    value: str

class RobotAPI:
    """
    API client for MiR robots
    """
    
    GOTO_GUID: str = "mirconst-guid-0000-0001-actionlist00"
    GOTO_CHARGER_GUID: str = "mirconst-guid-0000-0004-actionlist00"
    DEFAULT_MAP: str = "/v2.0.0/maps/6bad8aa5-b6e0-11ef-9eaa-b46921170fcf"
    
    def __init__(self, robot_type: RobotType = RobotType.SUPERMAN) -> None:
        self._headers: Dict[str, str] = {
            "Authorization": "Basic ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA==",
            "Content-Type": "application/json",
            "Language": "en_US"
        }
        self.robot_type: str = robot_type.value[0]
        self._base_url: str = robot_type.value[1]
        self.positions_robot: Dict[str, str] = {}
        self.missions_robot: Dict[str, str] = {}
        
        # Initialize data
        self._load_initial_data()

    def _load_initial_data(self) -> None:
        """
        Load initial positions and missions data
        """

        self.get_missions()
        self.get_positions()

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Make an HTTP request to the robot API
        
        Args:
            method: HTTP method to use
            endpoint: API endpoint
            data: Optional data to send with the request
            
        Returns:
            Response object from the request
            
        Raises:
            requests.RequestException: If the request fails
        """

        url = urljoin(self._base_url, endpoint)
        
        request_methods: Dict[str, Callable] = {
            'GET': requests.get,
            'POST': requests.post,
            'DELETE': requests.delete,
            'PUT': requests.put
        }
        
        if method not in request_methods:
            raise ValueError(f"Invalid HTTP method: {method}")
            
        try:
            return request_methods[method](
                url=url,
                headers=self._headers,
                json=data
            )
        except requests.RequestException as e:
            raise requests.RequestException(f"Request failed: {str(e)}")

    def get_missions(self) -> List[str]:
        """
        Get available mission names from the robot.
        
        Returns:
            List of mission names
            
        Raises:
            requests.RequestException: If the request fails
        """

        try:
            response = self._make_request('GET', "missions")
            response.raise_for_status()
            
            missions: List[Mission] = response.json()
            self.missions_robot = {mission["name"]: mission["guid"] for mission in missions}
            
            return list(self.missions_robot.keys())
            
        except requests.RequestException as e:
            print(f"Error fetching missions: {str(e)}")
            return []

    def get_positions(self) -> List[str]:
        """
        Get configured position names from the robot
        
        Returns:
            List of position names
            
        Raises:
            requests.RequestException: If the request fails
        """

        try:
            response = self._make_request('GET', "positions")
            response.raise_for_status()

            if self.robot_type == "mir200" or self.robot_type == "mir100": type_ids = [0, 7]
            else: type_ids = [0, 20]
            
            positions: List[Position] = response.json()
            self.positions_robot = {
                pos["name"]: [pos["guid"], pos["type_id"]]
                for pos in positions
                if pos["type_id"] in type_ids and pos["map"] == self.DEFAULT_MAP
            }
            return list(self.positions_robot.keys())
            
        except requests.RequestException as e:
            print(f"Error fetching positions: {str(e)}")
            return []

    def execute_mission(self, mission_name: str) -> bool:
        """
        Execute a specific mission
        
        Args:
            mission_name: Name of the mission to execute
            
        Returns:
            True if mission was sent successfully, False otherwise
        """

        if mission_name not in self.missions_robot:
            print(f"Mission '{mission_name}' not found")
            return False
            
        try:
            response = self._make_request(
                'POST', 
                "mission_queue",
                {"mission_id": self.missions_robot[mission_name]}
            )
            response.raise_for_status()
            
            print(f"Mission '{mission_name}' sent successfully to robot")
            return True
            
        except requests.RequestException as e:
            print(f"Error executing mission: {str(e)}")
            return False

    def go_to(self, position_name: str) -> bool:
        """
        Send robot to a specific position
        
        Args:
            position_name: Name of the position to go to
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        
        if position_name not in self.positions_robot:
            print(f"Position '{position_name}' not found")
            return False
        
        mission_id = self.GOTO_GUID if self.positions_robot[position_name][1] == 0 else self.GOTO_CHARGER_GUID
        position_id = "Position" if mission_id == self.GOTO_GUID else "chargingStationPosition"

        try:
            body = {
                "mission_id": mission_id,
                "parameters": [
                    MissionParameter(
                        id=position_id,
                        value=self.positions_robot[position_name][0]
                    ).__dict__
                ]
            }
            response = self._make_request('POST', 'mission_queue', body)
            response.raise_for_status()
            
            print(f"Robot sent to position '{position_name}'")
            return True
            
        except requests.RequestException as e:
            print(f"Error sending robot to position: {str(e)}")
            return False