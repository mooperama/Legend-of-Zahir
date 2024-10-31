import json
import os
from datetime import datetime
from enemies import Enemy
from typing import Dict, List, Optional

class ZahirSaveSystem:
    def __init__(self, save_dir: str = "saves"):
        """Initialize the save system with specified directory."""
        self.save_dir = save_dir
        self.leaderboard_file = os.path.join(save_dir, "leaderboard.json")
        self._ensure_save_directory()
        
    def _ensure_save_directory(self):
        """Create save directory if it doesn't exist."""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def save_game(self, game_instance) -> str:
        """
        Save the current game state.
        
        Args:
            game_instance: The Game class instance containing current game state
            
        Returns:
            The path to the save file
        """
        # Generate save name with timestamp
        save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Collect player data
        player_data = {
            "name": game_instance.player_name,
            "health": game_instance.player.health,
            "exp": game_instance.player.exp,
            "level": game_instance.player.level,
            "position": {
                "x": game_instance.player.rect.x,
                "y": game_instance.player.rect.y
            }
        }
        
        # Collect game progress data
        game_data = {
            "current_sequence_index": game_instance.current_sequence_index,
            "elapsed_time": game_instance.elapsed_time,
            "tutorial_completed": not game_instance.in_tutorial,
        }
        
        # Collect enemy data
        enemy_data = [{
            "position": {"x": enemy.rect.x, "y": enemy.rect.y},
            "health": enemy.health if hasattr(enemy, 'health') else 100
        } for enemy in game_instance.enemies]
        
        # Create complete save data
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "player": player_data,
            "game_state": game_data,
            "enemies": enemy_data
        }
        
        # Save to file
        save_path = os.path.join(self.save_dir, f"{save_name}.json")
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=4)
            
        # Update leaderboard if game is complete
        if game_instance.current_sequence_index >= game_instance.total_sequences:
            self.update_leaderboard(
                player_name=game_instance.player_name,
                time=game_instance.elapsed_time,
                score=game_instance.player.exp
            )
            
        return save_path

    def load_game(self, save_name: str, game_instance) -> bool:
        """
        Load a saved game state.
        
        Args:
            save_name: Name of the save file to load
            game_instance: The Game class instance to load data into
            
        Returns:
            bool: True if load successful, False otherwise
        """
        save_path = os.path.join(self.save_dir, f"{save_name}.json")
        
        if not os.path.exists(save_path):
            return False
            
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            # Restore player data
            game_instance.player_name = save_data["player"]["name"]
            game_instance.player.health = save_data["player"]["health"]
            game_instance.player.exp = save_data["player"]["exp"]
            game_instance.player.level = save_data["player"]["level"]
            game_instance.player.rect.x = save_data["player"]["position"]["x"]
            game_instance.player.rect.y = save_data["player"]["position"]["y"]
            
            # Restore game state
            game_instance.current_sequence_index = save_data["game_state"]["current_sequence_index"]
            game_instance.elapsed_time = save_data["game_state"]["elapsed_time"]
            game_instance.in_tutorial = not save_data["game_state"]["tutorial_completed"]
            
            # Clear and restore enemies
            game_instance.enemies.empty()
            for enemy_data in save_data["enemies"]:
                enemy = Enemy.create_random(game_instance)
                enemy.rect.x = enemy_data["position"]["x"]
                enemy.rect.y = enemy_data["position"]["y"]
                if hasattr(enemy, 'health'):
                    enemy.health = enemy_data["health"]
                game_instance.enemies.add(enemy)
                game_instance.allsprites.add(enemy)
            
            return True
            
        except Exception as e:
            print(f"Error loading save file: {e}")
            return False

    def list_saves(self) -> List[Dict]:
        """
        Return a list of all available save files with metadata.
        
        Returns:
            List of dictionaries containing save file information
        """
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json') and filename != "leaderboard.json":
                path = os.path.join(self.save_dir, filename)
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        saves.append({
                            "filename": filename,
                            "player_name": data["player"]["name"],
                            "timestamp": data["timestamp"],
                            "player_level": data["player"]["level"],
                            "elapsed_time": data["game_state"]["elapsed_time"]
                        })
                except:
                    continue
        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)

    def update_leaderboard(self, player_name: str, time: float, score: int):
        """
        Update the leaderboard with a new score.
        
        Args:
            player_name: Name of the player
            time: Total time taken
            score: Player's final score/exp
        """
        leaderboard = self.get_leaderboard()
        
        # Add new entry
        leaderboard.append({
            "name": player_name,
            "time": round(time, 2),
            "score": score,
            "date": datetime.now().isoformat()
        })
        
        # Sort by score (higher is better) and time (lower is better)
        leaderboard.sort(key=lambda x: (-x["score"], x["time"]))
        leaderboard = leaderboard[:10]  # Keep top 10
        
        with open(self.leaderboard_file, 'w') as f:
            json.dump(leaderboard, f, indent=4)

    def get_leaderboard(self) -> List[Dict]:
        """
        Get the current leaderboard.
        
        Returns:
            List of dictionary entries containing player info and scores
        """
        if not os.path.exists(self.leaderboard_file):
            return []
            
        try:
            with open(self.leaderboard_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def auto_save(self, game_instance):
        """
        Create an auto-save of the current game state.
        
        Args:
            game_instance: The Game class instance to save
        """
        save_name = "autosave"
        save_path = os.path.join(self.save_dir, f"leaderboard.json")
        
        # Use the same save logic as manual save
        self.save_game(game_instance)
        
        # Copy the latest save to autosave slot
        latest_save = max(
            [f for f in os.listdir(self.save_dir) if f.startswith("save_")],
            key=lambda f: os.path.getmtime(os.path.join(self.save_dir, f))
        )
        with open(os.path.join(self.save_dir, latest_save), 'rb') as src:
            with open(save_path, 'wb') as dst:
                dst.write(src.read())