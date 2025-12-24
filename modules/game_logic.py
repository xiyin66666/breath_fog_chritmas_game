"""
Game logic control module
Manage game state and flow
"""
import time

class GameLogic:
    def __init__(self):
        """Initialize game logic"""
        # Game states
        self.states = {
            "WAITING": "Waiting for breath",
            "FOG_COVERING": "Fog covering",
            "FOG_CLEARING": "Clearing fog",
            "TREE_REVEALED": "Tree revealed"
        }
        
        # Current state
        self.current_state = "WAITING"
        
        # Fog level
        self.fog_level = 0.0
        
        # State transition parameters
        self.o_mouth_duration = 0.0  # O mouth duration
        self.o_mouth_threshold = 1.0  # O mouth duration threshold to trigger fog (seconds)
        
        # Fog growth parameters
        self.fog_growth_rate = 0.015  # Fog growth rate per frame
        self.max_fog_level = 0.8      # Maximum fog level
        
        # Time recording
        self.last_update_time = time.time()
        self.state_start_time = time.time()
        
        # Hand detection history
        self.hand_detected_history = []
        self.hand_history_max_len = 10
        
    def update(self, mouth_is_o, hands_detected, hand_positions):
        """
        Update game state
        
        Args:
            mouth_is_o: Whether O mouth is detected
            hands_detected: Whether hands are detected
            hand_positions: List of hand positions
            
        Returns:
            current_state: Current game state
            fog_level: Current fog level
        """
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update hand detection history
        self.hand_detected_history.append(hands_detected)
        if len(self.hand_detected_history) > self.hand_history_max_len:
            self.hand_detected_history.pop(0)
        
        # State machine logic
        if self.current_state == "WAITING":
            self.update_waiting_state(mouth_is_o, delta_time)
        
        elif self.current_state == "FOG_COVERING":
            self.update_fog_covering_state(delta_time)
        
        elif self.current_state == "FOG_CLEARING":
            self.update_fog_clearing_state(hands_detected, delta_time)
        
        elif self.current_state == "TREE_REVEALED":
            self.update_tree_revealed_state()
        
        return self.current_state, self.fog_level
    
    def update_waiting_state(self, mouth_is_o, delta_time):
        """Update waiting state"""
        if mouth_is_o:
            # Increase O mouth duration
            self.o_mouth_duration += delta_time
            
            # If duration reaches threshold, switch to fog covering state
            if self.o_mouth_duration >= self.o_mouth_threshold:
                self.current_state = "FOG_COVERING"
                self.state_start_time = time.time()
                self.o_mouth_duration = 0.0
                print("State transition: Waiting -> Fog covering")
        else:
            # Reset O mouth duration
            self.o_mouth_duration = 0.0
        
        # Reset fog level
        self.fog_level = 0.0
    
    def update_fog_covering_state(self, delta_time):
        """Update fog covering state"""
        # Increase fog level
        self.fog_level += self.fog_growth_rate
        
        # Limit fog level
        if self.fog_level >= self.max_fog_level:
            self.fog_level = self.max_fog_level
            self.current_state = "FOG_CLEARING"
            self.state_start_time = time.time()
            print("State transition: Fog covering -> Clearing fog")
    
    def update_fog_clearing_state(self, hands_detected, delta_time):
        """Update clearing fog state"""
        # If hands detected, decrease fog level
        if hands_detected:
            self.fog_level -= self.fog_growth_rate * 2  # Clear faster than growth
        
        # If fog completely cleared, switch to tree revealed state
        if self.fog_level <= 0.0:
            self.fog_level = 0.0
            self.current_state = "TREE_REVEALED"
            self.state_start_time = time.time()
            print("State transition: Clearing fog -> Tree revealed")
    
    def update_tree_revealed_state(self):
        """Update tree revealed state"""
        # Maintain current state until game reset
        pass
    
    def get_state_duration(self):
        """Get current state duration"""
        return time.time() - self.state_start_time
    
    def reset(self):
        """Reset game"""
        self.current_state = "WAITING"
        self.fog_level = 0.0
        self.o_mouth_duration = 0.0
        self.state_start_time = time.time()
        print("Game reset")
    
    def get_state_description(self):
        """Get current state description"""
        return self.states.get(self.current_state, "Unknown state")